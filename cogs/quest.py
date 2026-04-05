# This file is part of NeuraSelf-UwU.
# Copyright (c) 2025-Present Routo
#
# NeuraSelf-UwU is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with NeuraSelf-UwU. If not, see <https://www.gnu.org/licenses/>.

import asyncio
import re
import time
import core.state as state
from discord.ext import commands

import random

class Quest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = True
        self.task = None
        self.active_resolutions = set()
        self.last_parse_time = 0

    async def register_actions(self):
        cfg = self.bot.config.get('commands', {}).get('quest', {})
        if cfg.get('enabled', True):
            self.bot.log("SYS", "Quest Module configured.")
            ih = cfg.get('interval_h', 6)
            # Phase 15: Quest Interval Jitter
            delay = (ih * 3600) + random.randint(-1800, 1800)
            await self.bot.neura_register_command("quest", "quest", priority=4, delay=delay, initial_offset=random.uniform(120, 600))
            self.trigger_action()

    def trigger_action(self):
        cfg = self.bot.config.get('commands', {}).get('quest', {})
        ih = cfg.get('interval_h', 6)
        
        if 'quest' in self.bot.cmd_states:
            # Phase 15: Quest Interval Jitter
            self.bot.cmd_states['quest']['delay'] = (ih * 3600) + random.randint(-1800, 1800)

    @commands.Cog.listener()
    async def on_message(self, message):
        core_config = self.bot.config.get('core', {})
        monitor_id = str(core_config.get('monitor_bot_id', '408785106942164992'))
        
        if str(message.author.id) != monitor_id:
            return
        if self.bot.owo_user is None:
            self.bot.owo_user = message.author
        all_channels = [str(c) for c in self.bot.channels]
        if str(message.channel.id) not in all_channels:
            return

        full_text = self.bot.get_full_content(message)

        if "quest log" in full_text or "checklist" in full_text:
            is_for_me = self.bot.is_message_for_me(message, role="header")
            
            if not is_for_me:
                return
            
            # Debounce rapid firing (wait 10s between full parses)
            if time.time() - self.last_parse_time < 10:
                return
            self.last_parse_time = time.time()
            
            self._parse_quests(full_text)

    def _parse_quests(self, text):
        progress_pattern = r'progress:\s*\[(\d+)/(\d+)\]'
        timer_pattern = r'next quest in:\s*(\d+h \d+m \d+s)'
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        new_quest_data = []
        
        st = self.bot.stats
        old_quests = st.get('quest_data', [])
        
        for i, line in enumerate(lines):
            match = re.search(progress_pattern, line)
            if match:
                current = int(match.group(1))
                total = int(match.group(2))
                
                desc = "Unknown Quest"
                for j in range(i-1, max(-1, i-4), -1):

                    raw_line = lines[j]

                    if any(x in raw_line.lower() for x in ["progress:", "quest log", "belong to", "next quest"]):
                        continue
                    desc_part = raw_line
                    if "reward:" in raw_line.lower():
                        parts = re.split(r'reward:', raw_line, flags=re.IGNORECASE)
                        desc_part = parts[0]

                    clean_desc = desc_part.replace(':blank:', '').replace('‣', '').replace('*', '').strip()
                    clean_desc = re.sub(r'^\d+[\)\.]\s*', '', clean_desc) 
                    clean_desc = re.sub(r'<[^>]*>', '', clean_desc)
                    clean_desc = clean_desc.replace('`', '').strip() 
                    
                    if clean_desc and len(clean_desc) > 3:
                        desc = clean_desc
                        break
                
                quest_item = {
                    'description': desc,
                    'current': current,
                    'total': total,
                    'completed': current >= total
                }
                new_quest_data.append(quest_item)
                
                if quest_item['completed']:
                    was_completed = any(q['description'] == desc and q.get('completed') for q in old_quests)
                    if not was_completed:
                        self.bot.log("SUCCESS", f"QUEST COMPLETED: {desc}")
                elif current < total:
                    # Attempt to resolve action / say quests
                    if desc not in self.active_resolutions:
                        asyncio.create_task(self._auto_resolve_quest(desc, total - current))

        timer_match = re.search(timer_pattern, text)
        next_timer = timer_match.group(1).upper() if timer_match else None
        
        st['quest_data'] = new_quest_data
        st['next_quest_timer'] = next_timer
        
        if new_quest_data:
            self.bot.log("SYS", f"Dashboard synced: {len(new_quest_data)} quests tracked.")
        elif "quest log" in text:
            self.bot.log("DEBUG", "Regex failure: Found 'Quest Log' but couldn't parse progress lines.")

    async def _auto_resolve_quest(self, desc, remaining):
        cfg = self.bot.config.get('commands', {}).get('quest', {})
        if not cfg.get('auto_checklist', True): return
        
        self.active_resolutions.add(desc)
        try:
            desc_lower = desc.lower()
        
            if "say 'owo'" in desc_lower or "say owo" in desc_lower:
                self.bot.log("SYS", f"Smart Quest: Queuing {min(remaining, 5)} 'owo' messages.")
                for _ in range(min(remaining, 5)):
                    await self.bot.neura_enqueue("owo", priority=2)
                    await asyncio.sleep(random.uniform(5, 12))
            
            elif "use an action command" in desc_lower:
                actions = ["hug", "kiss", "cuddle", "pat", "slap", "punch", "bite", "lick"]
                action = random.choice(actions)
                # Find a random valid channel and fetch recent users
                if not self.bot.channels: return
                try:
                    channel = self.bot.get_channel(int(self.bot.channels[0]))
                    if channel:
                        history = [msg async for msg in channel.history(limit=20)]
                        target = random.choice([m.author for m in history if m.author.id != self.bot.user.id and not m.author.bot])
                        
                        self.bot.log("SYS", f"Smart Quest: Action queued ('owo {action} @{target.name}')")
                        await self.bot.neura_enqueue(f"owo {action} <@{target.id}>", priority=2)
                except Exception as e:
                    self.bot.log("ERROR", f"Failed to get target for action quest: {e}")
        except Exception as e:
            self.bot.log("ERROR", f"Quest automation error: {e}")
        finally:
            # Allow refiring after a short wait to ensure owo bot processed the previous ones
            await asyncio.sleep(60) 
            if desc in self.active_resolutions:
                self.active_resolutions.remove(desc)

async def setup(bot):
    cog = Quest(bot)
    await bot.add_cog(cog)