
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


# Slot index → gem type name (official mapping, 4 slots)
SLOT_NAMES = ["huntGem", "empoweredGem", "luckyGem", "specialGem"]

# OwO slot number (1-4) → slot name
SLOT_NUMBER_TO_NAME = {1: "huntGem", 2: "empoweredGem", 3: "luckyGem", 4: "specialGem"}

# OwO gem emoji name suffix → slot index
# NOTE: OwO names slot2 gems as '{rarity}star', NOT '{rarity}gem2'
GEM_EMOJI_TO_SLOT = {
    "gem1": 0,   # huntGem
    "star": 1,   # empoweredGem  ← OwO calls these 'star' gems
    "gem3": 2,   # luckyGem
    "gem4": 3,   # specialGem
}

# OwO rarity prefix in gem emoji codes → tier name
GEM_RARITY_PREFIX = {'c': 'common', 'u': 'uncommon', 'r': 'rare', 'e': 'epic', 'm': 'mythical', 'l': 'legendary', 'f': 'fabled'}

# Tier order: highest rarity first
TIER_PRIORITY = ['fabled', 'legendary', 'mythical', 'epic', 'rare', 'uncommon', 'common']

class NeuraGems(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = True
        self.last_full_sync = 0 # Phase 31: 4H Safety Sync
        
        # gem_tiers[tier][slot_index] = gem_id
        # Slot order: [huntGem(gem1), empoweredGem(star), luckyGem(gem3), specialGem(gem4)]
        # Confirmed from real inventory: cstar=079, ustar=080, rstar=081 (star=slot2/empoweredGem)
        self.gem_tiers = {
            "fabled":    ["057", "085", "071", "078"],  # gem1, star, gem3, gem4
            "legendary": ["056", "084", "070", "077"],
            "mythical":  ["055", "083", "069", "076"],
            "epic":      ["054", "082", "068", "075"],
            "rare":      ["053", "081", "067", "074"],
            "uncommon":  ["052", "080", "066", "073"],
            "common":    ["051", "079", "065", "072"],
        }
        
        # gem_slot_status[slot_name] = True (active) / False (empty/expired)
        # Initialized as None = unknown, wait for a hunt message to confirm
        self.gem_slot_status: dict = {s: None for s in SLOT_NAMES}

        self.last_inv_time: float = 0

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def convert_small_numbers(self, text):
        mapping = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
        nums = "".join(filter(str.isdigit, text.translate(mapping)))
        return int(nums) if nums else 0

    def find_gems_available(self, content):
        """
        Parse OwO inventory message into {gem_id: count} dict.
        Supports both superscript and standard numeric counts.
        """
        # Phase 31: Robust Regex for both superscript and standard numbers
        matches = re.findall(
            r'`(\d{3})`<a?:([cfelmru])(gem[134]|star):\d+>([⁰¹²³⁴⁵⁶⁷⁸⁹\d]+)',
            content,
            re.IGNORECASE
        )
        available = {}
        for item_id, rarity_prefix, gem_type, count_str in matches:
            count = self.convert_small_numbers(count_str)
            if count == 0: # Try standard int if superscript failed
                try:
                    nums = "".join(filter(str.isdigit, count_str))
                    count = int(nums) if nums else 0
                except: continue
            
            if count > 0:
                available[item_id] = count
        return available

    def _slot_has_any_in_inventory(self, slot_idx: int, inv: dict) -> bool:
        """Return True if inventory has at least one gem for this slot (any rarity)."""
        for tier in TIER_PRIORITY:
            tier_ids = self.gem_tiers.get(tier, [])
            if slot_idx < len(tier_ids):
                if inv.get(tier_ids[slot_idx], 0) > 0:
                    return True
        return False

    def _best_gem_for_slot(self, slot_idx: int, available: dict, tier_cfg: dict) -> str | None:
        """Return the gem_id of the highest enabled rarity for this slot, or None."""
        for tier in TIER_PRIORITY:
            if not tier_cfg.get(tier, True):
                continue
            tier_ids = self.gem_tiers.get(tier, [])
            if slot_idx >= len(tier_ids):
                continue
            gem_id = tier_ids[slot_idx]
            if available.get(gem_id, 0) > 0:
                available[gem_id] -= 1  # mark as consumed
                return gem_id
        return None

    def build_equip_list(self, empty_slots: list[str], available: dict) -> list[str]:
        """
        For each empty slot (by name), find the best available gem.
        Returns list of gem_ids to equip (strip leading zeros for the command).
        """
        cnf = self.bot.config.get('commands', {}).get('gems', {})
        tier_cfg = cnf.get('tiers', {})
        to_equip = []
        for slot_name in empty_slots:
            idx = SLOT_NAMES.index(slot_name) if slot_name in SLOT_NAMES else -1
            if idx < 0:
                continue
            gem_id = self._best_gem_for_slot(idx, available, tier_cfg)
            if gem_id:
                to_equip.append(gem_id)
        return to_equip

    # -----------------------------------------------------------------------
    # Active Gem Detection from hunt embed
    # -----------------------------------------------------------------------

    def _parse_active_slots_from_hunt(self, message) -> dict[int, str]:
        """
        Parse OwO's hunt message to find which gem slots are currently active.

        OwO hunt format uses Discord custom emoji or text names:
            <:cgem1:id>[23/25] or :cgem1:[23/25]
            <:cstar:id>[10/15] or :cstar:[10/15]

        Returns dict of {slot_index (0-3): rarity_prefix str} for ACTIVE slots.
        """
        text = self.bot.get_full_content(message)
        # Matches both <:cgem1:id> and :cgem1: format
        # Group 1: Rarity prefix, Group 2: Gem type name
        matches = re.findall(
            r'[:<]a?:([cfelmru])(gem[134]|star)(?::\d+)?[>:]',
            text,
            re.IGNORECASE
        )
        active = {}
        for rarity_prefix, gem_type in matches:
            slot_idx = GEM_EMOJI_TO_SLOT.get(gem_type.lower())
            if slot_idx is not None:
                active[slot_idx] = rarity_prefix.lower()
        return active

    # -----------------------------------------------------------------------
    # Event listeners
    # -----------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_message(self, message):
        monitor_id = str(self.bot.config.get('core', {}).get('monitor_bot_id', '408785106942164992'))
        if str(message.author.id) != monitor_id:
            return

        cnf = self.bot.config.get('commands', {}).get('gems', {})
        if not cnf.get('enabled', True):
            return

        all_channels = [str(c) for c in self.bot.channels]
        if str(message.channel.id) not in all_channels:
            return

        content = self.bot.get_full_content(message)
        lower = content.lower()
        is_for_me = self.bot.is_message_for_me(message)

        # ── Lootbox received: clear inventory snapshot so we re-check ──
        if is_for_me and ("found a" in lower or "received a" in lower) and "lootbox" in lower:
            state.gem_inventory_cache.pop(self.bot.user_id, None)
            self.gem_slot_status = {s: None for s in SLOT_NAMES}
            self.bot.log("SYS", "[NeuraGems] Lootbox received. Resetting gem state for fresh check.")
            return

        # ── Gem activation confirmation ──
        activation_match = re.search(r":(\w+): \| .* activated a\(n\) (.*) gem!", lower)
        if activation_match:
            gem_name = activation_match.group(2).lower()
            g_type = None
            if "empowering" in gem_name: g_type = "empoweredGem"
            elif "hunting" in gem_name: g_type = "huntGem"
            elif "lucky" in gem_name: g_type = "luckyGem"
            elif "special" in gem_name: g_type = "specialGem"
            if g_type:
                self.gem_slot_status[g_type] = True
                uid = str(self.bot.user.id) if self.bot.user else self.bot.user_id
                if uid not in state.account_stats:
                    state.account_stats[uid] = state.get_empty_stats()
                state.account_stats[uid]['gems_used'] = state.account_stats[uid].get('gems_used', 0) + 1
                # Remove from missing cache
                state.missing_gems_cache.setdefault(self.bot.user_id, [])
                state.missing_gems_cache[self.bot.user_id] = [
                    g for g in state.missing_gems_cache[self.bot.user_id] if g != g_type
                ]
                state.checking_gems[self.bot.user_id] = False
                self.bot.log("SUCCESS", f"[NeuraGems] Slot '{g_type}' confirmed active.")
            return

        # ── Hunt message: determine which slots are active / empty ──
        # Phase 31: Decoupled from "empowered by" string to detect 0-gem states
        if (("caught" in lower or "found" in lower or "gained" in lower) and is_for_me and "hunt is " in lower):
            # If the specific "empowered by" string is missing, it means 0 gems are active
            if "empowered by" not in lower:
                active_slot_map = {}
            else:
                active_slot_map = self._parse_active_slots_from_hunt(message)
                
            active_slot_names = {SLOT_NAMES[idx] for idx in active_slot_map if idx < len(SLOT_NAMES)}
            
            type_cfg = cnf.get('types', {})
            enabled_slots = [s for s in SLOT_NAMES if type_cfg.get(s, s != "specialGem")]

            # Update per-slot status based on presence/absence in the hunt message
            for slot in enabled_slots:
                if slot in active_slot_names:
                    self.gem_slot_status[slot] = True
                else:
                    # Slot is enabled but NOT in the hunt message → confirmed empty
                    self.gem_slot_status[slot] = False

            # Log active slots with rarity for visibility
            for idx, rarity_p in active_slot_map.items():
                slot_name = SLOT_NAMES[idx] if idx < len(SLOT_NAMES) else f"slot{idx}"
                rarity_name = GEM_RARITY_PREFIX.get(rarity_p, rarity_p)
                self.bot.log("INFO", f"[NeuraGems] Slot {idx+1} ({slot_name}): {rarity_name} gem active.")

            # Find which enabled slots are confirmed empty
            empty_slots = [s for s in enabled_slots if self.gem_slot_status.get(s) is False]

            if not empty_slots:
                return  # All slots filled, nothing to do

            now = time.time()
            if now - self.last_inv_time < 15:
                return  # Debounce

            worth_checking = []
            now = time.time()
            
            # Phase 31: Passive Sync - triggered by any 'owo inv' response (handled in inventory block below)
            for slot in empty_slots:
                if slot in missing_cache:
                    continue  # Already know we have none
                idx = SLOT_NAMES.index(slot)
                if not inv_cache:
                    worth_checking.append(slot)  # No snapshot yet, check once
                elif self._slot_has_any_in_inventory(idx, inv_cache):
                    # Cache says we HAVE gems! Use them now
                    to_equip = self.build_equip_list([slot], dict(inv_cache))
                    if to_equip:
                        # Update cache and send use command immediately
                        for gid in to_equip: inv_cache[gid] = max(0, inv_cache.get(gid, 1)-1)
                        cmd_ids = [gid.lstrip('0') or '0' for gid in to_equip]
                        use_cmd = f"owo use {' '.join(cmd_ids)}"
                        self.bot.log("SUCCESS", f"[NeuraGems] Instant Use (Cache Sync): {use_cmd}")
                        await asyncio.sleep(random.uniform(3.0, 7.0))
                        await self.bot.neura_enqueue(use_cmd, priority=2)
                    continue
                else:
                    worth_checking.append(slot)

            if not worth_checking:
                return

            if state.checking_gems.get(self.bot.user_id):
                return

            state.checking_gems[self.bot.user_id] = {"time": now, "types": worth_checking}
            self.last_inv_time = now
            self.bot.log("SYS", f"[NeuraGems] Empty slots: {worth_checking}. Fetching inventory...")
            await asyncio.sleep(random.uniform(6.0, 15.0))
            await self.bot.neura_enqueue("owo inv", priority=2)
            return

        # ── Inventory response: snapshot + equip ──
        if not is_for_me:
            return
        if ("'s inventory" in lower or "'s gems" in lower) and "**" in lower:
            # Passive / Direct Inventory Update
            gem_info = state.checking_gems.get(self.bot.user_id) or {}
            target_slots = gem_info.get("types", list(SLOT_NAMES))
            state.checking_gems[self.bot.user_id] = False

            # Parse and snapshot
            available = self.find_gems_available(message.content)
            state.gem_inventory_cache[self.bot.user_id] = dict(available)
            self.bot.log("SYS", f"[NeuraGems] Inventory snapshot updated ({len(available)} gem types).")

            # Determine which target slots still have no gems at all
            type_cfg = cnf.get('types', {})
            still_missing = []
            for slot in target_slots:
                idx = SLOT_NAMES.index(slot) if slot in SLOT_NAMES else -1
                if idx < 0:
                    continue
                if self._slot_has_any_in_inventory(idx, available):
                    # Clear from missing cache
                    state.missing_gems_cache.setdefault(self.bot.user_id, [])
                    state.missing_gems_cache[self.bot.user_id] = [
                        g for g in state.missing_gems_cache[self.bot.user_id] if g != slot
                    ]
                else:
                    still_missing.append(slot)

            # Try opening lootboxes if some slots still have no gems
            if still_missing:
                lb_count = available.get("050", available.get("50", 0))
                if lb_count > 0:
                    self.bot.log("SYS", f"[NeuraGems] Slots {still_missing} empty, but {lb_count} lootboxes found. Opening...")
                    await asyncio.sleep(random.uniform(2.0, 4.0))
                    await self.bot.neura_enqueue("owo lb all", priority=2)
                    # Re-check inventory after opening
                    state.checking_gems[self.bot.user_id] = {"time": time.time(), "types": still_missing}
                    await asyncio.sleep(random.uniform(5.0, 8.0))
                    await self.bot.neura_enqueue("owo inv", priority=2)
                else:
                    for slot in still_missing:
                        mc = state.missing_gems_cache.setdefault(self.bot.user_id, [])
                        if slot not in mc:
                            mc.append(slot)
                            self.bot.log("WARN", f"[NeuraGems] No gems available for slot '{slot}'. Suppressing future checks.")

            # ── Build equip command for all fillable slots ──
            fillable_slots = [s for s in target_slots if s not in still_missing]
            if fillable_slots:
                to_equip = self.build_equip_list(fillable_slots, dict(available))
                if to_equip:
                    # Phase 31: Decrement local cache to keep it accurate
                    inv_cache = state.gem_inventory_cache.get(self.bot.user_id, {})
                    for gid in to_equip:
                        if gid in inv_cache and inv_cache[gid] > 0:
                            inv_cache[gid] -= 1

                    # Strip leading zeros for command arg
                    cmd_ids = [gid.lstrip('0') or '0' for gid in to_equip]
                    use_cmd = f"owo use {' '.join(cmd_ids)}"
                    self.bot.log("SUCCESS", f"[NeuraGems] Equipping {len(to_equip)} gem(s): {use_cmd}")
                    await asyncio.sleep(random.uniform(4.0, 10.0))
                    await self.bot.neura_enqueue(use_cmd, priority=2)
                    self.last_inv_time = time.time()
                    self.last_full_sync = time.time() # Reset sync timer on success
                else:
                    self.bot.log("WARN", "[NeuraGems] Inventory checked but find_gems_to_use returned empty.")

    async def register_actions(self):
        cnf = self.bot.config.get('commands', {}).get('gems', {})
        if cnf.get('enabled', True):
            interval_cfg = cnf.get('sync_interval', [1200, 1800])
            if isinstance(interval_cfg, list) and len(interval_cfg) == 2:
                interval = random.uniform(interval_cfg[0], interval_cfg[1])
            else:
                interval = float(interval_cfg)
            
            # Phase 34: Proactive Gem Sync (Guaranteed inventory checks)
            await self.bot.neura_register_command("gem_sync", "owo inv", priority=2, delay=interval, initial_offset=random.uniform(60, 300))
            self.bot.log("SYS", f"[NeuraGems] Proactive Sync enabled (Interval: {round(interval/60, 1)}m)")

async def setup(bot):
    cog = NeuraGems(bot)
    await bot.add_cog(cog)
