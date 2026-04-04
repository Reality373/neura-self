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

from discord.ext import commands
import asyncio
import time
import random
import re
import json
import os

class NeuraCursePray(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.state_file = "data/cp_state.json"
        self.last_run = self._load_last_run()

    def _load_last_run(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                    self.last_target = data.get("cp_last_target")
                    return data.get("cp_last_run", 0)
            except:
                pass
        self.last_target = None
        return 0

    def _save_last_run(self):
        data = {}
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
            except:
                pass
        data["cp_last_run"] = self.last_run
        data["cp_last_target"] = self.last_target
        with open(self.state_file, "w") as f:
            json.dump(data, f)

    def trigger_action(self):
        cmds_cfg = self.bot.config.get("commands", {})
        curse_cfg = cmds_cfg.get("curse", {})
        pray_cfg = cmds_cfg.get("pray", {})
        
        available = []
        if curse_cfg.get("enabled", False): available.append("curse")
        if pray_cfg.get("enabled", False): available.append("pray")
        
        if available:
            # Phase 17: Moody Mood Bias (Curse vs Pray based on sleepiness)
            # Late-night/Early-morning users are more likely to curse (cranky)
            current_hour = time.localtime().tm_hour
            if current_hour in [0, 1, 2, 3, 4, 22, 23]:
                # Cranky mood
                choice = random.choices(available, weights=[70, 30] if "curse" in available and "pray" in available else None)[0]
            else:
                # Kind mood
                choice = random.choices(available, weights=[30, 70] if "curse" in available and "pray" in available else None)[0]
            
            cfg = curse_cfg if choice == "curse" else pray_cfg
            
            raw_targets = cfg.get("targets", [])
            if not isinstance(raw_targets, list):
                raw_targets = [raw_targets]
                
            targets = [str(t).strip() for t in raw_targets if t and str(t).strip()]
                
            if targets:
                # Phase 17: Target Affinity (70% chance for friend/rival)
                if self.last_target in targets and random.random() < 0.70:
                    target = self.last_target
                    self.bot.log("STEALTH", f"Social Affinity Triggered: Targeting {target} again.")
                else:
                    target = random.choice(targets)
                
                self.last_target = target
                if cfg.get("ping", True):
                    full_cmd = f"{choice} <@{target}>"
                else:
                    full_cmd = f"{choice} {target}"
            else:
                full_cmd = choice
            
            self.bot.cmd_states['cursepray']['content'] = full_cmd

            # Phase 17: Social Timing Jitter (300 - 450s)
            cur_cooldown = random.uniform(300, 450)
            self.bot.cmd_states['cursepray']['delay'] = cur_cooldown


    @commands.Cog.listener()
    async def on_message(self, message):
        await self._process_response(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self._process_response(after)

    async def _process_response(self, message):
        core_config = self.bot.config.get("core", {})
        monitor_id = str(core_config.get("monitor_bot_id", "408785106942164992"))
        if str(message.author.id) != monitor_id:
            return
        if message.channel.id != self.bot.channel_id:
            return
            
        full_content = self.bot.get_full_content(message)
        
        is_for_me = self.bot.is_message_for_me(message)
        
        success_triggers = [
            "puts a curse on", "is now cursed.",
            "prays for", "prays..."
        ]
        
        if is_for_me and any(t in full_content for t in success_triggers):
            self.last_run = time.time()
            self._save_last_run()
            self.bot.log("SUCCESS", "Curse/Pray action confirmed, cooldown reset.")

    async def register_actions(self):
        cmds_cfg = self.bot.config.get("commands", {})
        if cmds_cfg.get("curse", {}).get("enabled", False) or cmds_cfg.get("pray", {}).get("enabled", False):
            self.bot.log("SYS", "NeuraCursePray Module configured.")
            
            # Phase 17: Social Jitter Startup (45s - 150s)
            startup_offset = random.uniform(45, 150)
            await self.bot.neura_register_command("cursepray", "curse", priority=3, delay=delay, initial_offset=startup_offset)
            self.trigger_action()

async def setup(bot):
    cog = NeuraCursePray(bot)
    await bot.add_cog(cog)
