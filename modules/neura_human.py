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
import random
import time
import traceback

class NeuraHuman:
    last_break_check = time.time()
    break_lock = asyncio.Lock()
    is_on_break = False
    current_interval = None

    @staticmethod
    async def neura_send(bot, channel, content):
        start_time = time.time()
        
        stealth_cfg = bot.config.get('stealth', {})
        if not isinstance(stealth_cfg, dict): stealth_cfg = {}
        
        from modules.stealth_circadian import handle_circadian_rhythm
        from modules.stealth_typo import apply_typo_logic

        await handle_circadian_rhythm(bot, stealth_cfg)
        
        if bot.is_on_break:
            bot.log("STEALTH", "Executing during break (Priority/Bypass action)...")

        # Phase 23: Post-Captcha Stress Scaling
        stress_active = time.time() < bot.stress_until
        
        # Phase 18: Burnout scaling (Distraction chance)
        session_duration = time.time() - bot.start_time
        persona = getattr(bot, 'session_persona', 'CASUAL')
        mode = getattr(bot, 'session_mode', 'CASUAL')
        
        lurk_chance = 0.02
        if session_duration > 14400: # 4 Hours
            lurk_chance = 0.10
            
        if persona == 'GRINDER' and mode == 'BINGE':
            lurk_chance = 0.001
        elif persona == 'GRINDER':
            lurk_chance = 0.005
            
        if stress_active:
             lurk_chance *= 3 # 3x distraction chance while stressed
             if random.random() < 0.001:
                  bot.log("STEALTH", "Stress Logic: Human is nervous after captcha. Skips increased.")
                 
        if random.random() < lurk_chance:
            lurk_duration = random.randint(60, 180)
            bot.log("STEALTH", f"Lurking (Stress={stress_active}): Human is distracted for {lurk_duration}s...")
            await asyncio.sleep(lurk_duration)
        
        hb_cfg = stealth_cfg.get('human_break', {})
        hb_enabled = hb_cfg.get('enabled', True)
        
        def get_val(v, default=10):
            if isinstance(v, list):
                return random.uniform(v[0], v[1])
            return v

        hb_duration = get_val(hb_cfg.get('duration_min', 10), 10) * 60
        hb_base_interval = get_val(hb_cfg.get('interval_min', 45), 45) * 60
        
        if persona == 'GRINDER':
            hb_duration *= 0.3 # 70% shorter breaks
            hb_base_interval *= 2.5 # Wait 2.5x longer between breaks
        
        if bot.current_break_interval is None:
            bot.current_break_interval = hb_base_interval * (1 + random.uniform(-0.15, 0.15))
            
        hb_interval = bot.current_break_interval

        runtime = time.time() - bot.last_break_check
        if hb_enabled and runtime > hb_interval: 
            async with bot.break_lock:
                if time.time() - bot.last_break_check > hb_interval and not bot.is_on_break:
                    bot.is_on_break = True
                    start_break_time = time.time()
                    bot.log("STEALTH", f"Pausing for {int(hb_duration/60)}mins (Break Time)")
                    
                    async def break_task_runner():
                        try:
                            while bot.is_on_break:
                                curr_stealth = bot.config.get('stealth', {})
                                curr_hb = curr_stealth.get('human_break', {})
                                
                                if not curr_hb.get('enabled', True):
                                    bot.log("STEALTH", "Break interrupted: Human Break disabled in settings.")
                                    break
                                
                                raw_dur = curr_hb.get('duration_min', 10)
                                curr_duration = (random.uniform(raw_dur[0], raw_dur[1]) if isinstance(raw_dur, list) else raw_dur) * 60
                                if time.time() - start_break_time >= curr_duration:
                                    break
                                    
                                await asyncio.sleep(1)
                        finally:
                            bot.last_break_check = time.time()
                            bot.is_on_break = False
                            bot.current_break_interval = hb_base_interval * (1 + random.uniform(-0.15, 0.15))
                            bot.session_mode = random.choices(['BINGE', 'CASUAL'], weights=[0.4, 0.6])[0]
                            bot.log("STEALTH", f"Break finished. Simulating app warmup (5-12s)...")
                            await asyncio.sleep(random.uniform(5.0, 12.0))
                            bot.log("STEALTH", f"Warmup finished. Resuming operations. Mode: {bot.session_mode}")
                    
                    asyncio.create_task(break_task_runner())
                elif bot.is_on_break:
                     pass
                        
        if bot.session_mode == 'CASUAL' or stress_active:
            casual_delay = random.uniform(1.0, 5.0)
            await asyncio.sleep(casual_delay)

        config = stealth_cfg.get('typing', {})
        if not isinstance(config, dict):
            config = {}

        if not config.get('enabled', False):
            try:
                await channel.send(content)
                return True
            except:
                return False
        
        reaction_min = config.get('reaction_min', 1.0)
        reaction_max = config.get('reaction_max', 3.0)
        mistake_rate = config.get('mistake_rate', 5)
        
        # Undefined variable fixes
        lazy_typo_rate = config.get('lazy_typo_rate', 0.2)
        extra_delay = config.get('extra_delay', 0.1)

        platform_delay_mult = 1.0
        platform_error_mult = 1.0
        if bot.is_mobile:
            platform_delay_mult = 1.3
            platform_error_mult = 1.2
            
        intensity_factor = 1.0
        mode = bot.session_mode

        
        if mode == 'BINGE':
            intensity_factor = 0.7 # Faster reactions (0.7x delay)
            mistake_rate = mistake_rate * 2 * platform_error_mult # 2x typo rate
        elif mode == 'CASUAL':
            intensity_factor = 1.3 # Slower, deliberate
            mistake_rate = mistake_rate * 0.5 * platform_error_mult # Lower typo rate
        else:
            mistake_rate = mistake_rate * platform_error_mult
            
        # Phase 7: Determine fatigue overhead (configurable via fatigue_simulation)
        fatigue_cfg = stealth_cfg.get('session', {}).get('fatigue_simulation', {})
        max_fatigue_delay = fatigue_cfg.get('slowdown_factor', 1.2) - 1.0  # Convert 1.2x to +0.2s max overhead
        burnout_mins = fatigue_cfg.get('burnout_rest_min', [20, 40])
        burnout_threshold = (random.uniform(burnout_mins[0], burnout_mins[1]) if isinstance(burnout_mins, list) else burnout_mins) * 60 * 60 / 10  # Convert to seconds of session time
        session_duration = time.time() - getattr(bot, 'start_time', time.time())
        fatigue_factor = min(max_fatigue_delay, (session_duration / max(1, burnout_threshold)) * max_fatigue_delay) 

        reaction_time = (random.uniform(reaction_min, reaction_max) * intensity_factor * platform_delay_mult)
        
        # Phase 22: Desktop Window Focus Delay (2-5s)
        # First message after a long break or startup on Desktop
        if not bot.is_mobile and time.time() - getattr(bot, 'last_sent_time', 0) > 600:
             plat_cfg = bot.config.get('platform_settings', {})
             refocus_range = plat_cfg.get('desktop_refocus_delay', [2, 5])
             refocus_delay = random.uniform(refocus_range[0], refocus_range[1]) if isinstance(refocus_range, list) else random.uniform(2, 5)
             reaction_time += refocus_delay
             bot.log("STEALTH", f"Desktop: Simulating window refocus delay (+{round(refocus_delay, 1)}s)")
        
        # Apply fatigue to initial reaction
        reaction_time += fatigue_factor

        if reaction_time > 0.1:
            await asyncio.sleep(reaction_time)

        # Phase 22: Desktop Clipboard Pasting (70% chance for long content)
        if not bot.is_mobile and len(content) > 15 and random.random() < 0.70:
             paste_delay = random.uniform(1.2, 2.5)
             await asyncio.sleep(paste_delay)
             bot.log("STEALTH", "Desktop: Simulating clipboard paste (instant send).")
             await channel.send(content)
             return True

        try:
            async with channel.typing():
                chars = list(str(content))
                i = 0
                typo_count = 0
                
                start_time = time.time()
                
                burst_count = 0
                max_burst = random.randint(2, 4)
                
                while i < len(chars):
                    char = chars[i]
                    
                    # Determine delay for this character
                    if burst_count < max_burst:
                        delay = random.uniform(0.01, 0.03) # fast burst
                        burst_count += 1
                    else:
                        delay = random.uniform(0.1, 0.25) # human pause after burst
                        burst_count = 0
                        max_burst = random.randint(2, 4)

                    if char in ".,!?;": delay += random.uniform(0.2, 0.4)
                    
                    # Handle typos and visible corrections (Phase 9)
                    old_char = chars[i]
                    typo_count = await apply_typo_logic(chars, i, mistake_rate, lazy_typo_rate, typo_count)
                    
                    if chars[i] == old_char and random.random() < 0.15:
                        # simulate a "near miss" (backspace and fix)
                        await asyncio.sleep(random.uniform(0.4, 0.8))

                    await asyncio.sleep(delay)
                    i += 1
                    

                
                final_content = "".join(chars)
                enter_delay = random.uniform(0.3, 0.7) + (random.uniform(0, extra_delay) if isinstance(extra_delay, (int, float)) and extra_delay > 0 else 0)
                await asyncio.sleep(enter_delay)
                
                total_time = round(time.time() - start_time, 2)
                if typo_count > 0:
                    bot.log("STEALTH", f"Typing: {total_time}s (Simulated {typo_count} typos)")
                
                await channel.send(final_content)
                return True
        except Exception:
            try:
                await channel.send(content)
                return True
            except Exception as final_e:
                bot.log("ERROR", f"Critical send failure: {final_e}")
                return False
    
    @staticmethod
    def neura_calculate_typing_speed(text, wpm=55):
        return (len(text) / 5) / wpm * 60