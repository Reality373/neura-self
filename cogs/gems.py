
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
import random
import core.state as state
from discord.ext import commands

class NeuraGems(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = True
        
        self.gem_tiers = {
            "fabled": ["057", "071", "078", "085"],
            "legendary": ["056", "070", "077", "084"],
            "mythical": ["055", "069", "076", "083"],
            "epic": ["054", "068", "075", "082"],
            "rare": ["053", "067", "074", "081"],
            "uncommon": ["052", "066", "073", "080"],
            "common": ["051", "065", "072", "079"],
        }
        
        self.inventory_check = False
        self.last_inv_time = 0

    def convert_small_numbers(self, text):
        mapping = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
        nums = "".join(filter(str.isdigit, text.translate(mapping)))
        return int(nums) if nums else 0

    def find_gems_available(self, content):
        matches = re.findall(r"(?:`|\*\*)?(\d{2,3})(?:`|\*\*)?.*?([⁰¹²³⁴⁵⁶⁷⁸⁹0-9]+)", content)
        available = {}
        for gid, count_str in matches:
            if gid.isdigit(): 
                available[gid] = self.convert_small_numbers(count_str)
        return available

    def find_gems_to_use(self, available, target_types=None):
        cnf = self.bot.config.get('commands', {}).get('gems', {})
        tier_cfg = cnf.get('tiers', {})
        type_cfg = cnf.get('types', {})
        order_cfg = cnf.get('order', {})
        use_set = cnf.get('use_gems_set', False)

        tier_priority = ['fabled', 'legendary', 'mythical', 'epic', 'rare', 'uncommon', 'common']
        if order_cfg.get('lowestToHighest', False):
            tier_priority.reverse()

        desired_types = []
        if target_types:
            desired_types = target_types
        else:
            if type_cfg.get('huntGem', True): desired_types.append('huntGem')
            if type_cfg.get('empoweredGem', True): desired_types.append('empoweredGem')
            if type_cfg.get('luckyGem', True): desired_types.append('luckyGem')
            if type_cfg.get('specialGem', False): desired_types.append('specialGem')

        type_to_index = {
            "huntGem": 0,
            "empoweredGem": 1, 
            "luckyGem": 2,
            "specialGem": 3
        }

        if use_set:
            for tier in tier_priority:
                if not tier_cfg.get(tier, True): continue
                
                tier_ids = self.gem_tiers.get(tier)
                if not tier_ids: continue

                has_all_in_tier = True
                temp_selection = []
                
                for g_type in desired_types:
                    idx = type_to_index.get(g_type)
                    if idx is None or idx >= len(tier_ids): 
                        has_all_in_tier = False
                        break
                    
                    gem_id = tier_ids[idx]
                    if available.get(gem_id, 0) < 1:
                        has_all_in_tier = False
                        break
                    temp_selection.append(gem_id)
                
                if has_all_in_tier:
                    for g in temp_selection:
                        available[g] -= 1
                    return temp_selection

        gems_to_equip = []
        for g_type in desired_types:
            idx = type_to_index.get(g_type)
            if idx is None: continue

            for tier in tier_priority:
                if not tier_cfg.get(tier, True): continue
                
                tier_ids = self.gem_tiers.get(tier)
                if not tier_ids or idx >= len(tier_ids): continue
                
                gem_id = tier_ids[idx]
                if available.get(gem_id, 0) > 0:
                    gems_to_equip.append(gem_id)
                    available[gem_id] -= 1
                    break
        
        return gems_to_equip if gems_to_equip else None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != 408785106942164992:
            return
        
        cfg = self.bot.config.get('commands', {}).get('gems', {})
        if not cfg.get('enabled', True):
            return

        all_channels = [str(c) for c in self.bot.channels]
        if str(message.channel.id) not in all_channels:
            return

        content = message.content.lower()
        is_for_me = self.bot.is_message_for_me(message)
        
        if not is_for_me and (time.time() - self.bot.last_sent_time) < 5:
             if "hunt" in self.bot.last_sent_command.lower() or "inv" in self.bot.last_sent_command.lower() or "gems" in self.bot.last_sent_command.lower():
                 is_for_me = True

        if not is_for_me:
            return

        if ("found a" in content or "received a" in content) and "lootbox" in content:
            if self.bot.user_id in state.missing_gems_cache and state.missing_gems_cache[self.bot.user_id]:
                self.bot.log("SYS", "[NeuraGems] Lootbox acquired! Resetting missing gems cache to re-check on next hunt.")
                state.missing_gems_cache[self.bot.user_id] = []

        if ("caught" in content or "found" in content) and "hunt is empowered by" not in content:
            now = time.time()
            if now - self.last_inv_time > 15:
                cnf = self.bot.config.get('commands', {}).get('gems', {})
                type_cfg = cnf.get('types', {})
                missing_types = [t for t, enabled in type_cfg.items() if enabled]
                
                if missing_types:
                    actually_missing = [t for t in missing_types if t not in state.missing_gems_cache.get(self.bot.user_id, [])]
                    
                    if actually_missing:
                        if state.checking_gems.get(self.bot.user_id):
                            return

                        self.last_inv_time = now
                        
                        self.bot.log("SYS", "[NeuraGems] No active gems. Human is checking inventory...")
                        await asyncio.sleep(random.uniform(6.0, 15.0))
                        await self.bot.neura_enqueue("owo inv", priority=2)
            return

        activation_match = re.search(r":(\w+): \| .* activated a\(n\) (.*) gem!", content)
        if activation_match:
            gem_emoji = activation_match.group(1)
            gem_name = activation_match.group(2).lower()
            
            g_type = None
            if "empowering" in gem_name: g_type = "empoweredGem"
            elif "hunting" in gem_name: g_type = "huntGem"
            elif "lucky" in gem_name: g_type = "luckyGem"
            elif "special" in gem_name: g_type = "specialGem"
            
            if g_type:
                import core.state as state
                if self.bot.user:
                    uid = str(self.bot.user.id)
                    if uid not in state.account_stats: state.account_stats[uid] = state.get_empty_stats()
                    state.account_stats[uid]['gems_used'] = state.account_stats[uid].get('gems_used', 0) + 1
                    
                if self.bot.user_id not in state.missing_gems_cache:
                    state.missing_gems_cache[self.bot.user_id] = []
                
                if g_type in state.missing_gems_cache[self.bot.user_id]:
                    state.missing_gems_cache[self.bot.user_id].remove(g_type)
                
                self.bot.log("SUCCESS", f"[NeuraGems] Confirmation: {g_type} activated. Cache updated.")

                self.last_inv_time = time.time()
                state.checking_gems[self.bot.user_id] = False
                return

        if "hunt is empowered by" in content:
            active_gems = []
            if "gem1" in content: active_gems.append("huntGem")
            if "gem3" in content: active_gems.append("empoweredGem")
            if "gem4" in content: active_gems.append("luckyGem")
            if "star" in content: active_gems.append("specialGem")

            cnf = self.bot.config.get('commands', {}).get('gems', {})
            type_cfg = cnf.get('types', {})
            
            missing_types = []
            if type_cfg.get('huntGem', True) and "huntGem" not in active_gems: missing_types.append("huntGem")
            if type_cfg.get('empoweredGem', True) and "empoweredGem" not in active_gems: missing_types.append("empoweredGem")
            if type_cfg.get('luckyGem', True) and "luckyGem" not in active_gems: missing_types.append("luckyGem")
            if type_cfg.get('specialGem', False) and "specialGem" not in active_gems: missing_types.append("specialGem")

            if missing_types:
                actually_missing = [t for t in missing_types if t not in [g['name'] if isinstance(g, dict) else g for g in state.missing_gems_cache.get(self.bot.user_id, [])]]
                
                if actually_missing:
                    # Phase 11: Clear old missing gems from cache (1h TTL)
                    cached_missing = state.missing_gems_cache.get(self.bot.user_id, [])
                    now = time.time()
                    state.missing_gems_cache[self.bot.user_id] = [
                        g for g in cached_missing 
                        if not isinstance(g, dict) or (now - g.get('time', 0)) < 3600
                    ]
                    
                    # Convert to simple list for checking
                    current_missing_names = [g['name'] if isinstance(g, dict) else g for g in state.missing_gems_cache[self.bot.user_id]]
                    
                    final_missing = [t for t in actually_missing if t not in current_missing_names]
                    
                    if final_missing:
                        if state.checking_gems.get(self.bot.user_id):
                            return
                        
                        self.bot.log("SYS", f"[NeuraGems] Gems missing: {', '.join(final_missing)}. Checking inventory...")
                        state.checking_gems[self.bot.user_id] = {
                            "time": time.time(),
                            "types": final_missing
                        }
                        await asyncio.sleep(random.uniform(6.0, 15.0))
                        await self.bot.neura_enqueue("owo inv", priority=2)
                else:
                    pass
            return

        if ("'s inventory" in content or "'s gems" in content) and "**" in content:
             if state.checking_gems.get(self.bot.user_id):
                if not self.bot.is_message_for_me(message, role="header"):
                    if not self.bot.is_message_for_me(message):
                        return

                gem_info = state.checking_gems.get(self.bot.user_id, {})
                missing_types = gem_info.get("types", ["huntGem", "empoweredGem", "luckyGem"])

                state.checking_gems[self.bot.user_id] = False
                
                available = self.find_gems_available(message.content)
                to_use = self.find_gems_to_use(available, target_types=missing_types)

                if self.bot.user_id not in state.missing_gems_cache:
                    state.missing_gems_cache[self.bot.user_id] = []
                

                type_to_index = {
                    "huntGem": 0,
                    "empoweredGem": 1, 
                    "luckyGem": 2,
                    "specialGem": 3
                }
                
  
                cnf = self.bot.config.get('commands', {}).get('gems', {})
                type_cfg = cnf.get('types', {})
                all_enabled_types = [t for t, enabled in type_cfg.items() if enabled]

                still_missing_after = []
                for g_type in all_enabled_types:
                    idx = type_to_index.get(g_type)
                    if idx is None: continue
                    
                    tier_priority = ['fabled', 'legendary', 'mythical', 'epic', 'rare', 'uncommon', 'common']
                    has_any = False
                    for tier in tier_priority:
                        tier_ids = self.gem_tiers.get(tier)
                        if not tier_ids or idx >= len(tier_ids): continue
                        gem_id = tier_ids[idx]
                        if available.get(gem_id, 0) > 0:
                            has_any = True
                            break
                    
                    if has_any:
                        # Clear from cache
                        state.missing_gems_cache[self.bot.user_id] = [g for g in state.missing_gems_cache[self.bot.user_id] if (g['name'] if isinstance(g, dict) else g) != g_type]
                        self.bot.log("SYS", f"[NeuraGems] {g_type} found in inventory, removed from missing cache.")
                    else:
                        still_missing_after.append(g_type)

                if still_missing_after:
                    lb_count = available.get("050", available.get("50", 0))
                    if lb_count > 0:
                        self.bot.log("SYS", f"[NeuraGems] Missing gems ({', '.join(still_missing_after)}), but found {lb_count} Lootboxes! Opening them...")
                        
                        await asyncio.sleep(random.uniform(2.0, 4.0))
                        await self.bot.neura_enqueue("owo lb all", priority=2)
                        
                        # Set checking gems again so the next owo inv triggers gem equipment
                        state.checking_gems[self.bot.user_id] = {
                            "time": time.time(),
                            "types": missing_types
                        }
                        
                        await asyncio.sleep(random.uniform(5.0, 8.0))
                        await self.bot.neura_enqueue("owo inv", priority=2)
                        
                        # Still equip whatever we found in this iteration before exiting
                        if to_use:
                            cmd_ids = [gid if not gid.startswith('0') else gid[1:] for gid in to_use]
                            use_cmd = f"owo use {' '.join(cmd_ids)}"
                            await asyncio.sleep(random.uniform(3.0, 6.0))
                            await self.bot.neura_enqueue(use_cmd, priority=2)
                            self.bot.log("SUCCESS", f"[NeuraGems] Equipped intermediate gems: {use_cmd}")
                        
                        return # wait for the next inventory check where it will equip the new gems and then cache if still missing!
                    else:
                        for g_type in still_missing_after:
                            current_missing_names = [g['name'] if isinstance(g, dict) else g for g in state.missing_gems_cache[self.bot.user_id]]
                            if g_type not in current_missing_names:
                                state.missing_gems_cache[self.bot.user_id].append({"name": g_type, "time": time.time()})
                                self.bot.log("WARN", f"[NeuraGems] {g_type} missing and no Lootboxes to open. Added to missing cache.")

                if to_use:
                    cmd_ids = [gid if not gid.startswith('0') else gid[1:] for gid in to_use]
                    use_cmd = f"owo use {' '.join(cmd_ids)}"
                    
                    self.bot.log("SUCCESS", f"[NeuraGems] Deliberating gem use: {use_cmd}")
                    await asyncio.sleep(random.uniform(6.0, 15.0))
                    await self.bot.neura_enqueue(use_cmd, priority=2)
                    self.bot.log("SUCCESS", f"[NeuraGems] Equipped: {use_cmd}")
                    self.last_inv_time = time.time()
                elif not still_missing_after:
                    self.bot.log("WARN", f"[NeuraGems] Inventory checked, but no gems missing or available to use.")

                pass

    async def register_actions(self):
        pass

async def setup(bot):
    cog = NeuraGems(bot)
    bot.add_listener(cog.on_message, 'on_message')
    await bot.add_cog(cog)
