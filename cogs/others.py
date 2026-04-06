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
import time
import re
import json
import random
import core.state as state
from discord.ext import commands

class Others(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_dict = {}
        self._weapon_ids: list = []       # parsed from owo w list
        self._last_weapon_list_time: float = 0.0
        self._weapon_check_interval: float = 3600.0  # once per hour
        
        try:
            with open("utils/emojis.json", 'r', encoding="utf-8") as file:
                self.emoji_dict = json.load(file)
        except:
            pass

    def get_emoji_names(self, text):
        pattern = re.compile(r"<a:[a-zA-Z0-9_]+:[0-9]+>|:[a-zA-Z0-9_]+:|[\U0001F300-\U0001F6FF\U0001F700-\U0001F77F]")
        emojis = pattern.findall(text)
        return [self.emoji_dict[char]["name"] for char in emojis if char in self.emoji_dict]

    async def _auto_accept_rules(self, message):
        all_channels = [str(c) for c in self.bot.channels]
        if str(message.channel.id) not in all_channels:
            return

        content = message.content.lower()
        if "**you must accept these rules to use the bot!**" in content:
            if message.components:
                await asyncio.sleep(random.uniform(0.6, 1.7))
                try:
                    comp = message.components[0]
                    if hasattr(comp, 'children'):
                        btn = comp.children[0]
                        if not btn.disabled:
                            scanning_delay = random.uniform(3.0, 12.0)
                            if random.random() < 0.10:
                                scanning_delay += 2.0
                            self.bot.log("STEALTH", f"Rule Acceptance: User is scanning rules ({round(scanning_delay, 1)}s)...")
                            await asyncio.sleep(scanning_delay)
                            await btn.click()
                            self.bot.log("SUCCESS", "Auto-Accepted OwO Rules")
                except Exception as e:
                    self.bot.log("ERROR", f"Failed to accept rules: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        await self._auto_accept_rules(message)

        monitor_id = str(self.bot.config.get('core', {}).get('monitor_bot_id', '408785106942164992'))
        if str(message.author.id) != monitor_id:
            return
        
        if self.bot.owo_user is None:
            self.bot.owo_user = message.author
        
        all_channels = [str(c) for c in self.bot.channels]
        if str(message.channel.id) not in all_channels:
            return

        content = message.content.lower()

        # --- Parse weapon list response (owo w with no args) ---
        # Each weapon line starts with a 6-char alphanumeric ID like "EA2FTF" or "DW2LLC"
        if self.bot.is_message_for_me(message):
            raw = message.content
            weapon_ids = re.findall(r'^([A-Z0-9]{6})\s+:', raw, re.MULTILINE)
            if weapon_ids and len(weapon_ids) >= 3:
                self._weapon_ids = weapon_ids
                self.bot.log("SYS", f"[WeaponCheck] Parsed {len(weapon_ids)} weapons from list.")
                # Now pick one and inspect it after a deliberation pause
                chosen = random.choice(weapon_ids)
                deliberation = random.uniform(4.0, 10.0)
                self.bot.log("STEALTH", f"[WeaponCheck] Scrolling to weapon {chosen} ({round(deliberation, 1)}s)...")
                await asyncio.sleep(deliberation)
                await self.bot.neura_enqueue(f"weapon {chosen}", priority=2)
                self.bot.log("CMD", f"[WeaponCheck] Checked weapon {chosen}")
                return

        # --- Cash balance update + trigger weapon list ---
        if "you currently have" in content and "cowoncy" in content:
            if not self.bot.is_message_for_me(message, role="header"):
                return
            try:
                cash_match = re.search(r'you currently have[^\d]*(\d{1,3}(?:,\d{3})*)', message.content.lower())
                if cash_match:
                    cash_str = cash_match.group(1).replace(',', '')
                    is_initial = self.bot.stats['current_cash'] is None
                    self.bot.stats['current_cash'] = int(cash_str)
                    self.bot.stats['last_cash_update'] = time.time()
                    state.record_snapshot(self.bot.user_id)
                    if is_initial:
                        self.bot.log("SYS", f"Initial Cash Balance synced: {cash_str} cowoncy")
                    else:
                        self.bot.log("INFO", f"Cash Updated: {cash_str} cowoncy")
            except:
                pass

            if not self.bot.is_message_for_me(message):
                return

            # Phase 28: Smart Weapon Check — fetch list first, inspect real ID
            now = time.time()
            if now - self._last_weapon_list_time > self._weapon_check_interval:
                self._last_weapon_list_time = now
                deliberation = random.uniform(4.0, 10.0)
                self.bot.log("STEALTH", f"[WeaponCheck] User is opening weapon inventory ({round(deliberation, 1)}s)...")
                await asyncio.sleep(deliberation)
                await self.bot.neura_enqueue("weapon", priority=2)
                self.bot.log("CMD", "[WeaponCheck] Requested weapon list (owo w)...")

    async def register_actions(self):
        pass

async def setup(bot):
    cog = Others(bot)
    await bot.add_cog(cog)
