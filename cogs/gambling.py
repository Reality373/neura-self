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
        self.last_cf_time = 0
        self.last_slots_time = 0

    def _get_next_bet(self, cfg, current_bet, won):
        # New explicit keys
        min_bet = cfg.get('min_bet')
        max_bet = cfg.get('max_bet')
        increase = cfg.get('increase')
        multiplier = cfg.get('multiplier', 1.0) # New multiplier key
        
        # Fallback to old 'amount' list if new keys missing
        if min_bet is None or max_bet is None:
            cfg_amount = cfg.get('amount', [100, 500])
            if isinstance(cfg_amount, list) and len(cfg_amount) >= 2:
                min_bet = int(cfg_amount[0])
                max_bet = int(cfg_amount[1])
            else:
                min_bet = int(cfg_amount) if cfg_amount else 100
                max_bet = min_bet * 10
        
        if increase is None:
            increase = 100 # Default increment

        min_bet, max_bet, increase = int(min_bet), int(max_bet), int(increase)
        multiplier = float(multiplier)

        if current_bet is None or won:
            # Start/Reset: Pick min or optional small random offset
            return min_bet
        else:
            # Loss: Multiply first, then add flat increase
            new_bet = int(current_bet * multiplier) + increase
            if new_bet > max_bet:
                new_bet = max_bet
            return new_bet

    def trigger_coinflip(self):
        cfg = self.bot.config.get('commands', {}).get('coinflip', {})
        
        if self.current_cf_bet is None:
            self.current_cf_bet = self._get_next_bet(cfg, None, True)

        amount = self.current_cf_bet
        side = cfg.get('side', 'h')
        
        # Phase 35: Sync speed with Dashboard
        delay_range = cfg.get('bet_delay', [10, 30])
        if isinstance(delay_range, list) and len(delay_range) == 2:
            delay = random.uniform(delay_range[0], delay_range[1])
        else:
            delay = float(delay_range)

        self.bot.cmd_states['coinflip']['content'] = f"cf {side} {amount}"
        self.bot.cmd_states['coinflip']['delay'] = delay
        self.bot.stats['coinflip_count'] = self.bot.stats.get('coinflip_count', 0) + 1
        self.bot.log("DEBUG", f"Next Coinflip prep: {side} {amount} in {round(delay,1)}s")
        self.last_cf_time = time.time()

    def trigger_slots(self):
        cfg = self.bot.config.get('commands', {}).get('slots', {})

        if self.current_slots_bet is None:
            self.current_slots_bet = self._get_next_bet(cfg, None, True)

        amount = self.current_slots_bet
        
        # Phase 35: Sync speed with Dashboard
        delay_range = cfg.get('bet_delay', [10, 30])
        if isinstance(delay_range, list) and len(delay_range) == 2:
            delay = random.uniform(delay_range[0], delay_range[1])
        else:
            delay = float(delay_range)

        self.bot.cmd_states['slots']['content'] = f"slots {amount}"
        self.bot.cmd_states['slots']['delay'] = delay
        self.bot.stats['slots_count'] = self.bot.stats.get('slots_count', 0) + 1
        self.bot.log("DEBUG", f"Next Slots prep: {amount} in {round(delay,1)}s")
        self.last_slots_time = time.time()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != int(self.bot.owo_bot_id): return
        if not self.bot.is_message_for_me(message): return
        
        # Phase 35: Use get_full_content to read Embeds + Text
        full_text = self.bot.get_full_content(message)
        now = time.time()
        
        # Phase 35: Result detection (Wait up to 45s for OwO response)
        if "you won" in full_text or "you lost" in full_text or "went with" in full_text or "nothing" in full_text or "spent" in full_text:
            
            # Coinflip Detection
            if self.last_cf_time != 0 and now - self.last_cf_time < 45:
                cfg = self.bot.config.get('commands', {}).get('coinflip', {})
                # Check for LOSS first
                if any(k in full_text for k in ["lost", "nothing", "spent"]):
                    self.bot.log("SUCCESS", f"Coinflip LOST ({self.current_cf_bet}). Next amount: {int(self.current_cf_bet * cfg.get('multiplier',2.0)) + cfg.get('increase',100)}")
                    self.current_cf_bet = self._get_next_bet(cfg, self.current_cf_bet, False)
                elif "won" in full_text:
                    self.bot.log("SUCCESS", f"Coinflip WON! Resetting bet.")
                    self.current_cf_bet = self._get_next_bet(cfg, self.current_cf_bet, True)
                
                self.last_cf_time = 0 
                self.trigger_coinflip() 
                    
            # Slots Detection
            elif self.last_slots_time != 0 and now - self.last_slots_time < 45:
                cfg = self.bot.config.get('commands', {}).get('slots', {})
                # Check for LOSS first
                if any(k in full_text for k in ["nothing", "lost", "spent"]):
                    self.bot.log("SUCCESS", f"Slots LOST ({self.current_slots_bet}). Next amount: {int(self.current_slots_bet * cfg.get('multiplier',2.0)) + cfg.get('increase',100)}")
                    self.current_slots_bet = self._get_next_bet(cfg, self.current_slots_bet, False)
                elif "won" in full_text:
                    if "nothing" in full_text: # Double safety for "won nothing"
                        self.current_slots_bet = self._get_next_bet(cfg, self.current_slots_bet, False)
                    else:
                        self.bot.log("SUCCESS", f"Slots WON! Resetting bet.")
                        self.current_slots_bet = self._get_next_bet(cfg, self.current_slots_bet, True)
                    
                self.last_slots_time = 0 
                self.trigger_slots() 

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