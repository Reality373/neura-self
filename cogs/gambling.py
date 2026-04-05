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
import random
import core.state as state
from discord.ext import commands

class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = True
        self.task = None
        self.current_cf_bet = None
        self.current_slots_bet = None

    def _get_next_bet(self, cfg_amount, current_bet, won):
        if not isinstance(cfg_amount, list) or len(cfg_amount) < 2:
            return int(cfg_amount) if cfg_amount else 1

        low = int(cfg_amount[0])
        high = int(cfg_amount[1])
        low_r = max(100, (low + 99) // 100 * 100)
        high_r = max(low_r, high // 100 * 100)

        if current_bet is None or won:
            range_total = high_r - low_r
            max_start = low_r + int(range_total * 0.3)
            max_start = max(low_r, max_start // 100 * 100)
            if max_start == low_r:
                return low_r
            steps = (max_start - low_r) // 100
            if steps <= 0: return low_r
            return low_r + random.randint(0, steps) * 100
        else:
            increase = random.randint(1, 3) * 100
            new_bet = current_bet + increase
            if new_bet > high_r:
                new_bet = high_r
            return new_bet

    def trigger_coinflip(self):
        cfg = self.bot.config.get('commands', {}).get('coinflip', {})
        
        if self.current_cf_bet is None:
            self.current_cf_bet = self._get_next_bet(cfg.get('amount', 1), None, True)

        amount = self.current_cf_bet
        side = cfg.get('side', 'h')
        
        self.bot.cmd_states['coinflip']['content'] = f"cf {side} {amount}"
        self.bot.cmd_states['coinflip']['delay'] = random.uniform(45, 180)
        self.bot.stats['coinflip_count'] = self.bot.stats.get('coinflip_count', 0) + 1

    def trigger_slots(self):
        cfg = self.bot.config.get('commands', {}).get('slots', {})

        if self.current_slots_bet is None:
            self.current_slots_bet = self._get_next_bet(cfg.get('amount', 1), None, True)

        amount = self.current_slots_bet
        
        self.bot.cmd_states['slots']['content'] = f"slots {amount}"
        self.bot.cmd_states['slots']['delay'] = random.uniform(45, 180)
        self.bot.stats['slots_count'] = self.bot.stats.get('slots_count', 0) + 1

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != int(self.bot.owo_bot_id): return
        if not self.bot.is_message_for_me(message): return
        
        content = message.content.lower()
        if "you won" in content or "you lost" in content or "went with" in content or "nothing" in content:
            if "coinflip" in self.bot.last_sent_command.lower() or "cf " in self.bot.last_sent_command.lower():
                cfg = self.bot.config.get('commands', {}).get('coinflip', {})
                if "won" in content:
                    self.current_cf_bet = self._get_next_bet(cfg.get('amount', 1), self.current_cf_bet, True)
                elif "lost" in content or "went with" in content:
                    self.current_cf_bet = self._get_next_bet(cfg.get('amount', 1), self.current_cf_bet, False)
                    
            elif "slots" in self.bot.last_sent_command.lower() or "s " in self.bot.last_sent_command.lower():
                cfg = self.bot.config.get('commands', {}).get('slots', {})
                if "won" in content:
                    self.current_slots_bet = self._get_next_bet(cfg.get('amount', 1), self.current_slots_bet, True)
                elif "nothing" in content or "lost" in content:
                    self.current_slots_bet = self._get_next_bet(cfg.get('amount', 1), self.current_slots_bet, False)

    async def register_actions(self):
        cfg_cf = self.bot.config.get('commands', {}).get('coinflip', {})
        if cfg_cf.get('enabled', False):
            self.bot.log("SYS", "Gambling (Coinflip) Module configured.")
            await self.bot.neura_register_command("coinflip", "cf", priority=3, delay=random.uniform(30, 60), initial_offset=15)
            self.trigger_coinflip()

        cfg_slots = self.bot.config.get('commands', {}).get('slots', {})
        if cfg_slots.get('enabled', False):
            self.bot.log("SYS", "Gambling (Slots) Module configured.")
            await self.bot.neura_register_command("slots", "slots", priority=3, delay=random.uniform(25, 50), initial_offset=20)
            self.trigger_slots()

async def setup(bot):
    cog = Gambling(bot)
    await bot.add_cog(cog)