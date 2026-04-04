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

import discord
from discord.ext import commands
import asyncio
import re
import time
import random
import core.state as state

class ResponseHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_success_time = {}
        self.success_triggers = {
            'hunt': ['you found:', 'you found', 'found:', 'is empowered by'],
            'battle': ['you won', 'you lost', 'goes into battle', 'battle!', 'won in', 'lost in', 'team gained', 'streak:', 'battle team gained', 'battle goes into', 'you won in', 'you lost in'],
            'curse': ['puts a curse on', 'is cursed', 'ghostly curse'],
            'pray': ['prays for', 'prays...'],
            'cookie': ['gave a cookie to', 'sent a cookie'],
            'daily': ['collected your daily', 'daily reward']
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        await self._process_response(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self._process_response(after)

    async def _process_response(self, message):
        if message.author.id == self.bot.user.id: return
        core_config = self.bot.config.get('core', {})
        monitor_id = str(core_config.get('monitor_bot_id', '408785106942164992'))
        if str(message.author.id) != monitor_id: return
        
        if self.bot.owo_user is None:
            self.bot.owo_user = message.author
        all_channels = [str(c) for c in self.bot.channels]
        if str(message.channel.id) not in all_channels:
            return
        

        full_content = self.bot.get_full_content(message)
        await self._handle_cooldowns(full_content, message)
        
        await self._handle_battle_results(full_content, message)
        
        if self.bot.is_message_for_me(message):
            await self._handle_success(full_content, message)
            await self._handle_status_updates(full_content, message)
        
        # New: Mention/Level Up awareness
        is_mention = f"<@{self.bot.user.id}>" in message.content or f"<@!{self.bot.user.id}>" in message.content
        is_level_up = "level up" in full_content and self.bot.is_message_for_me(message)
        
        if is_mention or is_level_up:
            wait = random.uniform(4.0, 10.0)
            self.bot.throttle_until = max(self.bot.throttle_until, time.time() + wait)
            reason = "Mentioned" if is_mention else "Level Up"
            self.bot.log("STEALTH", f"{reason} detected. Pausing {round(wait, 1)}s to 'read' message.")
            
            if random.random() < 0.20:
                emoji = random.choice(["🎉", "✨", "🔥", "🏆", "❤", "📈"])
                try:
                    await message.add_reaction(emoji)
                except:
                    pass
            
            # Phase 8: Text Response (10% chance)
            if is_level_up and random.random() < 0.10:
                await asyncio.sleep(random.uniform(1.5, 3.5))
                quotes = ["gg", "nice!", "level up!", "levels :)", "pog", "📈"]
                lq = self.bot.get_cog('LevelQuotes')
                if lq:
                    quotes.append(lq.get_random_quote(5, 50))
                
                await self.bot.neura_send(message.channel, random.choice(quotes))

    async def _handle_success(self, content, message):
        now = time.time()
        for cmd_type, triggers in self.success_triggers.items():
            if cmd_type == 'battle': continue 
            for trigger in triggers:
                if trigger in content:
                    if now - self.last_success_time.get(cmd_type, 0) < 5.0: break
                    self.last_success_time[cmd_type] = now
                    
                    if cmd_type == 'hunt':
                        self.bot.stats['hunt_count'] = self.bot.stats.get('hunt_count', 0) + 1
                        self.bot.log("SUCCESS", f"Hunt confirmed for {self.bot.display_name}")
                    elif cmd_type == 'curse':
                        if self.bot.is_message_for_me(message, role="source", keyword="puts a curse on"):
                            self.bot.log("SUCCESS", f"Curse confirmed for {self.bot.display_name}")
                        else: continue
                    elif cmd_type == 'pray':
                        if self.bot.is_message_for_me(message, role="source", keyword="prays for"):
                            self.bot.log("SUCCESS", f"Pray confirmed for {self.bot.display_name}")
                        else: continue
                    elif cmd_type == 'cookie':
                        if self.bot.is_message_for_me(message, role="target", keyword="got a cookie from"):
                            self.bot.log("SUCCESS", f"Cookie confirmed for {self.bot.display_name}")
                        else: continue
                    
                    # New: Rare animal reaction (Phase 10)
                    is_me = self.bot.is_message_for_me(message)
                    rare_keywords = ["fabled", "mythical", "legendary", "special", "gem"]
                    
                    if any(rk in content for rk in rare_keywords):
                        chance = 0.20 if is_me else 0.01 
                        if random.random() < chance:
                            emoji = random.choice(["😲", "🔥", "💎", "✨", "🙌", "👍", "👏"])
                            try:
                                await message.add_reaction(emoji)
                            except:
                                pass

    async def _handle_battle_results(self, content, message):
        is_battle_msg = any(trigger in content for trigger in ['goes into battle', 'battle!', 'won in', 'lost in', 'streak:', 'you won', 'you lost'])
        if not is_battle_msg: return

        is_for_me = self.bot.is_message_for_me(message)
        
        if is_for_me:
            now = time.time()
            if now - self.last_success_time.get('battle', 0) > 5.0:
                self.last_success_time['battle'] = now
                self.bot.stats['battle_count'] = self.bot.stats.get('battle_count', 0) + 1
                self.bot.log("SUCCESS", f"Battle confirmed for {self.bot.display_name}")
        else:
            pass

    async def _handle_cooldowns(self, content, message):
        if "slow down~" in content or "too fast for me" in content:
            # Phase 12: Frustration break after repeated throttles
            self.bot.stats['throttle_count'] = self.bot.stats.get('throttle_count', 0) + 1
            if self.bot.stats['throttle_count'] >= 3:
                wait_time = random.uniform(300.0, 900.0) # 5-15 mins
                self.bot.log("ALARM", f"Too many throttles ({self.bot.stats['throttle_count']}). Human is frustrated and taking a long break ({round(wait_time/60, 1)}m).")
                self.bot.stats['throttle_count'] = 0
            else:
                wait_time = random.uniform(15.0, 45.0) # Phase 8: Frustrated pause
            
            self.bot.throttle_until = time.time() + wait_time
            self.bot.log("STEALTH", f"Throttle: Human is pausing for {round(wait_time, 1)}s.")
            return True
            
        # Phase 24: "Early Bird" Timer Tracking & Precision Resends
        timer_match = re.search(r"please wait \*\*?(\d+)\*\*? seconds", content)
        if timer_match:
            seconds = int(timer_match.group(1))
            self.bot.log("STEALTH", f"Early Bird: OwO says wait {seconds}s. Scheduling precision resend...")
            
            # Find what we just sent
            last_cmd = getattr(self.bot, "last_sent_command", "").lower()
            if not last_cmd: return
            
            # Precision Wait: X + jitter(0.4-0.9s)
            precision_wait = seconds + random.uniform(0.4, 0.9)
            
            async def _precision_resend():
                # Phase 24: Anticipatory Ghost Typing (2s before timer)
                if precision_wait > 2.5:
                     await asyncio.sleep(precision_wait - 2.0)
                     self.bot.log("STEALTH", "Precision Wait: Hovering over keys (Ghost Typing)...")
                     async with message.channel.typing():
                         await asyncio.sleep(2.0)
                else:
                     await asyncio.sleep(precision_wait)
                
                self.bot.log("STEALTH", f"Precision Hit: Resending '{last_cmd}' exactly on time.")
                # Force resend without further scheduler overhead
                await self.bot.neura_send(message.channel, last_cmd)

            asyncio.create_task(_precision_resend())
            return True

    async def _handle_status_updates(self, content, message):
        # Phase 11: Human frustration on failed commands
        fail_triggers = ["you don't have any", "you need", "you are missing", "you cannot use"]
        if any(t in content for t in fail_triggers):
            wait = random.uniform(10.0, 25.0)
            self.bot.throttle_until = max(self.bot.throttle_until, time.time() + wait)
            self.bot.log("STEALTH", f"Command failed. Human is confused/checking reasons, pausing {round(wait, 1)}s.")
            return True
        pass

    async def _handle_ambient_social(self, message):
        """Phase 18: Conversational Mimicry (GG/lol reactions)"""
        # Achievement/failure keywords
        mimic_triggers = {
            "gg": ["won", "caught", "legendary", "fabled", "shiny", "gg"],
            "lol": ["lmao", "lol", "kappa", "funny"],
            "oof": ["lost", "missed", "died", "failed", "oof"],
            "nice": ["congrats", "congratulations", "nice"]
        }
        
        content = message.content.lower()
        for filler, keywords in mimic_triggers.items():
            if any(k in content for k in keywords):
                if random.random() < 0.002: # 0.2% chance
                    delay = random.uniform(2.5, 6.0)
                    await asyncio.sleep(delay)
                    self.bot.log("STEALTH", f"Ambient Mimicry: Reacting with '{filler}'")
                    await self.bot.neura_send(filler)
                    break

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id: return
        if message.author.bot: 
            await self._handle_ambient_social(message)
            return

        if message.guild and message.channel.id != self.bot.channel_id:
             # Basic ambient awareness even in other channels
             if random.random() < 0.0005: 
                 await self._handle_ambient_social(message)
             return

        await self._handle_ambient_social(message)

async def setup(bot):
    cog = ResponseHandler(bot)
    await bot.add_cog(cog)