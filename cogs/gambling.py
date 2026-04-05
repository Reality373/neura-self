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

def _pick_amount(cfg_amount):
    """Pick a random gambling amount from config.
    
    Supports:
      - int/float: single fixed amount (e.g. 400)
      - list [min, max]: random amount in multiples of 100 within range (e.g. [100, 1000])
    """
    if isinstance(cfg_amount, list) and len(cfg_amount) >= 2:
        low = int(cfg_amount[0])
        high = int(cfg_amount[1])
        # Round to nearest 100 boundaries
        low_r = max(100, (low + 99) // 100 * 100)   # round UP to nearest 100
        high_r = max(low_r, high // 100 * 100)       # round DOWN to nearest 100
        steps = (high_r - low_r) // 100 + 1
        return low_r + random.randint(0, steps - 1) * 100
    return int(cfg_amount) if cfg_amount else 1

class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = True
        self.task = None
        
    def trigger_coinflip(self):
        cfg = self.bot.config.get('commands', {}).get('coinflip', {})
        amount = _pick_amount(cfg.get('amount', 1))
        side = cfg.get('side', 'h')
        
        self.bot.cmd_states['coinflip']['content'] = f"cf {side} {amount}"
        self.bot.cmd_states['coinflip']['delay'] = random.uniform(45, 180)
        self.bot.stats['coinflip_count'] = self.bot.stats.get('coinflip_count', 0) + 1

    def trigger_slots(self):
        cfg = self.bot.config.get('commands', {}).get('slots', {})
        amount = _pick_amount(cfg.get('amount', 1))
        
        self.bot.cmd_states['slots']['content'] = f"slots {amount}"
        self.bot.cmd_states['slots']['delay'] = random.uniform(45, 180)
        self.bot.stats['slots_count'] = self.bot.stats.get('slots_count', 0) + 1

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