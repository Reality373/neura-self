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
from discord.ext import commands

class SellSac(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_sell_time: float = 0.0
        self.last_sac_time: float = 0.0
        self.next_sell_interval: float = 0.0
        self.next_sac_interval: float = 0.0
        self.loot_count = 0
        self.loot_threshold = random.randint(5, 15)
        self.task: asyncio.Task | None = None

    async def cog_load(self):
        self.task = asyncio.create_task(self.main_loop())

    async def cog_unload(self):
        if self.task:
            self.task.cancel()

    async def main_loop(self):
        while True:
            try:
                cfg = self.bot.config.get('commands', {}).get('sell_sac', {})
                sell_cfg = cfg.get('sell', {})
                sac_cfg = cfg.get('sacrifice', {})
                
                autosell_enabled = sell_cfg.get('enabled', False)
                autosac_enabled = sac_cfg.get('enabled', False)

                if not autosell_enabled and not autosac_enabled:
                    await asyncio.sleep(60)
                    continue

                now = time.time()
                
                if autosell_enabled:
                    if self.next_sell_interval == 0:
                        base_interval = sell_cfg.get('interval_min', 20) * 60
                        self.next_sell_interval = base_interval * (1 + random.uniform(-0.15, 0.15))

                    if now - self.last_sell_time > self.next_sell_interval:
                        await self._perform_human_sell(sell_cfg)
                        self.last_sell_time = now
                        self.next_sell_interval = 0 # reset for next calculation
                        self.bot.log("SYS", "Periodic AutoSell triggered.")

                if autosac_enabled:
                    if self.next_sac_interval == 0:
                        base_interval = sac_cfg.get('interval_min', 60) * 60
                        self.next_sac_interval = base_interval * (1 + random.uniform(-0.15, 0.15))

                    if now - self.last_sac_time > self.next_sac_interval:
                        await self._perform_human_sac(sac_cfg)
                        self.last_sac_time = now
                        self.next_sac_interval = 0 # reset
                        self.bot.log("SYS", "Periodic AutoSacrifice triggered.")

                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
    async def _perform_human_sell(self, sell_cfg):
        # Phase 27: Pre-Sell Inventory Check (15% chance)
        if random.random() < 0.15:
             check_cmd = random.choice(["owo inv", "owo zoo"])
             self.bot.log("STEALTH", f"Pre-Sell Check: User is checking {check_cmd} before selling...")
             await self.bot.neura_enqueue(check_cmd, priority=4)
             await asyncio.sleep(random.uniform(8.0, 20.0))
        
        # Phase 20: Deliberation Pause
        await asyncio.sleep(random.uniform(2, 5))
        await self.bot.neura_enqueue(f"sell {sell_cfg.get('type', 'all')}", priority=4)
        self.loot_count = 0
        self.loot_threshold = random.randint(5, 15)

    async def _perform_human_sac(self, sac_cfg):
        # Phase 27: Pre-Sacrifice Check (15% chance)
        if random.random() < 0.15:
             self.bot.log("STEALTH", "Pre-Sacrifice Check: User is checking zoo before sacrifice...")
             await self.bot.neura_enqueue("owo zoo", priority=4)
             await asyncio.sleep(random.uniform(8.0, 15.0))
             
        await asyncio.sleep(random.uniform(2, 5))
        cmd = "sc" if sac_cfg.get('use_shortform', False) else "sacrifice"
        await self.bot.neura_enqueue(f"{cmd} {sac_cfg.get('type', 'all')}", priority=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != 408785106942164992 or not self.bot.is_message_for_me(message):
            return
        
        if str(message.channel.id) not in [str(c) for c in self.bot.channels]:
            return

        if "you found:" in content:
            self.loot_count += 1
            if self.loot_count >= self.loot_threshold:
                if random.random() < 0.30: # 30% chance to trigger early
                    self.bot.log("STEALTH", f"Loot Trigger: Inventory feels full ({self.loot_count} hunts). Triggering early sell.")
                    cfg = self.bot.config.get('commands', {}).get('sell_sac', {}).get('sell', {})
                    if cfg.get('enabled', False):
                        asyncio.create_task(self._perform_human_sell(cfg))
                        self.last_sell_time = time.time()
                else:
                    # Didn't trigger, increase next threshold slightly
                    self.loot_threshold += random.randint(1, 3)

        if "you don't have enough cowoncy" in content or "you do not have enough cowoncy" in content:
            cfg = self.bot.config.get('commands', {}).get('sell_sac', {})
            sell_cfg = cfg.get('sell', {})
            if sell_cfg.get('enabled', False):
                # Phase 27: Frustration Pause (4s - 9s)
                frustration_delay = random.uniform(4.0, 9.0)
                self.bot.log("STEALTH", f"Low funds detected. Human is pausing for {round(frustration_delay, 1)}s in frustration.")
                await asyncio.sleep(frustration_delay)
                
                await self.bot.neura_enqueue(f"sell {sell_cfg.get('type', 'all')}", priority=2)
                self.last_sell_time = time.time()
                self.bot.log("SYS", "Frustrated AutoSell triggered.")

async def setup(bot):
    await bot.add_cog(SellSac(bot))
