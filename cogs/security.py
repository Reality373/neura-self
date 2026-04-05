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

import sys
import asyncio
import time
import random
import re
import os
import threading
import unicodedata
import requests
import json
import discord
from discord.ext import commands
from plyer import notification
import core.state as state

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        cfg = bot.config.get('security', {})
        self.enabled = cfg.get('enabled', True)
        self.notifications_enabled = cfg.get('notifications', {}).get('enabled', True)
        self.notification_title = cfg.get('notifications', {}).get('desktop', {}).get('title', "Neura Security Alert")
        self.webhook_url = cfg.get('webhook_url')
        self.monitor_id = str(bot.config.get('core', {}).get('monitor_bot_id', '408785106942164992'))
        self.beep_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "beeps", "security_beep.mp3")
        self.ban_keywords = [
            "youhavebeenbanned",
            "bannedforbotting",
            "bannedformacros"
        ]
        self.captcha_keywords = [
            "areyouarealhuman",
            "verifythatyouarehuman",
            "pleasecompletethiswithin",
            "pleaseusethelinkbelow",
            "completeyourcaptcha",
            "pleasedmmewiththefollowing",
            "pleasedmmewithonly",
            "ifyouhavetroublesolvingthecaptcha",
            "pleasecomplete",
            "tocheckthatyouareahuman",
            "tocheck",
            "human"
        ]
        self.warning_pattern = re.compile(r'\((\d+)/(\d+)\)')
        self.image_captcha_keywords = [
            "pleasedmme",
            "dmme",
            "beepboop",
            "checkthatyouareahuman",
            "solvingthecaptcha",
            "letterword"
        ]

    async def register_actions(self):
        cfg = self.bot.config.get('security', {})
        self.enabled = cfg.get('enabled', True)
        self.notifications_enabled = cfg.get('notifications', {}).get('enabled', True)
        self.notification_title = cfg.get('notifications', {}).get('desktop', {}).get('title', "Neura Security Alert")
        self.webhook_url = cfg.get('webhook_url')
        self.monitor_id = str(self.bot.config.get('core', {}).get('monitor_bot_id', '408785106942164992'))
        self.bot.log("SYS", "Security Module settings refreshed (Live Sync).")

    def _normalize(self, text):
        if not text:
            return ""
        text = unicodedata.normalize("NFKD", text)
        return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

    def _show_desktop_notification(self, message):
        if not self.notifications_enabled:
            return
        sec_cfg = self.bot.config.get('security', {})
        notif_cfg = sec_cfg.get('notifications', {})
        if self.bot.is_mobile:
            mobile = notif_cfg.get('mobile', {})
            if mobile.get('enabled', True):
                try:
                    os.system(f'termux-notification --title "{self.notification_title}" --content "{message}"')
                    vib = mobile.get('vibrate', True)
                    # Handle both bool and dict config formats safely
                    vib_enabled = vib if isinstance(vib, bool) else vib.get('enabled', True)
                    if vib_enabled:
                        raw_time = vib.get('time', 0.5) if isinstance(vib, dict) else 0.5
                        if isinstance(raw_time, list):
                            raw_time = random.uniform(raw_time[0], raw_time[1])
                        duration = int(raw_time * 1000)
                        os.system(f'termux-vibrate -d {duration}')

                    toast = mobile.get('toast', {})
                    if toast.get('enabled', True):
                        bg = toast.get('bg_color', 'black')
                        fg = toast.get('text_color', 'white')
                        pos = toast.get('position', 'middle')
                        os.system(f'termux-toast -b {bg} -c {fg} -g {pos} "{message}"')
                    tts = mobile.get('tts', {})
                    if tts.get('enabled', False):
                        os.system(f'termux-tts-speak "{message}"')
                except:
                    pass
            return
        desktop = notif_cfg.get('desktop', {})
        if desktop.get('enabled', True):
            try:
                notification.notify(title=self.notification_title, message=message, timeout=10)
            except:
                pass
    
    def _send_webhook(self, title, message):
        cfg = self.bot.config.get('security', {})
        wh_cfg = cfg.get('webhook', {})
        if not wh_cfg.get('enabled', True): return
        url = wh_cfg.get('url')
        if not url: return
        payload = {
            "content": "@everyone @here",
            "embeds": [{
                "title": title,
                "description": message,
                "color": 0xFF3B3B,
                "author": {
                    "name": f"NeuraSelf Security - {self.bot.username}",
                    "icon_url": "https://cdn.discordapp.com/attachments/1450161614375620802/1456632606002118657/neuralogo.png"
                },
                "footer": {"text": f"NeuraSelf • Account: {self.bot.username}"},
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S')
            }]
        }
        try:
            requests.post(url, json=payload, timeout=5)
        except:
            pass

    async def play_beep(self):
        def _play():
            if not os.path.exists(self.beep_file):
                return
            
            if self.bot.is_mobile:
                try:
                    os.system(f'termux-media-player play "{self.beep_file}"')
                except:
                    pass
                return

            try:
                 from playsound3 import playsound
                 playsound(self.beep_file, block=False)
            except:
                pass
        threading.Thread(target=_play, daemon=True).start()

    def _contains_keyword(self, text, keywords):
        cleaned = self._normalize(text)
        return any(k in cleaned for k in keywords)

    def _get_captcha_url(self, message):
        if not message.components:
            return None
        for comp in message.components:
            if not getattr(comp, "children", None): continue
            for child in comp.children:
                url = str(getattr(child, "url", "") or "")
                if "owobot.com/captcha" in url:
                    return url
        return None


    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.enabled: return
        if isinstance(message.channel, discord.DMChannel) and message.author.id == int(self.monitor_id):
            if (discord.utils.utcnow() - message.created_at).total_seconds() > 30: return
            if "i have verified that you are human" in message.content.lower():
                self.bot.log("SUCCESS", "Verified detected in DM. Captcha solved successfully. Simulating post-captcha fatigue...")
                
                # Phase 23: Post-Captcha Stress Mode (Adrenaline/Cautious)
                # Lasts for 20 minutes
                self.bot.stress_until = time.time() + 1200
                self.bot.log("STEALTH", "Stress Mode: Human is 'on edge' for 20 mins. Breaks/skips increased.")
                
                # Phase 23: DM Social Recognition (1% chance to react)
                if random.random() < 0.01:
                     await message.add_reaction(random.choice(["👍", "✅", "😰", "👌"]))
                
                stealth_cfg = self.bot.config.get('stealth', {})
                from modules.stealth_fatigue import apply_post_captcha_fatigue
                await apply_post_captcha_fatigue(self.bot, stealth_cfg)
                
                self.bot.paused = False
                self.bot.throttle_until = 0.0
                self.bot.last_sent_time = 0
                self.bot.warmup_until = 0
                
                grinding_cog = self.bot.get_cog('Grinding')
                if grinding_cog:
                    grinding_cog.cooldowns['hunt'] = 0
                    grinding_cog.cooldowns['battle'] = 0
                    grinding_cog.cooldowns['owo'] = 0
                
                self.bot.log("INFO", "All cooldowns reset. Bot resuming operations...")
                await asyncio.sleep(2)
                return

            if "letterword" in message.content.lower() and message.attachments:
                self.bot.log("SECURITY", "Detection AI: Letterword captcha identified in DMs.")
 
                count_match = re.search(r'(\d+)\s*letterword', message.content.lower())
                letter_count = int(count_match.group(1)) if count_match else 5
                
                image_url = message.attachments[0].url

                self.bot.log("SYS", f"Attempting to solve DM Captcha ({letter_count} letters)...")
                answer = await self.bot.captcha_solver.solve_image(image_url, letter_count)
                
                if answer:
                    self.bot.log("SUCCESS", f"AI Solver Answer: {answer}. Sending to OwO...")
                    await asyncio.sleep(random.uniform(10.0, 25.0)) # Increased DM switch delay
                    
                    # Phase 23: Captcha Uncertainty Simulation (4% chance to fail 1st attempt)
                    if random.random() < 0.04 and len(answer) > 2:
                         wrong_answer = answer[:-1] + random.choice("abcdefghijklmnopqrstuvwxyz")
                         self.bot.log("STEALTH", f"Uncertainty: Intentionally sending WRONG answer: {wrong_answer}")
                         async with message.channel.typing():
                             await asyncio.sleep(len(wrong_answer) * 0.15)
                             await message.channel.send(wrong_answer)
                         
                         await asyncio.sleep(random.uniform(3.0, 6.0))
                         self.bot.log("STEALTH", "Uncertainty: Correcting answer now...")

                    async with message.channel.typing():
                        await asyncio.sleep(len(answer) * 0.1)
                        await message.channel.send(answer)
                else:
                    self.bot.log("ERROR", "AI Solver failed to generate an answer.")
                    self._show_desktop_notification("AI Solver failed! Solve manually.")
                return

            captcha_url = self._get_captcha_url(message)
            if not captcha_url:
                url_match = re.search(r'https?://owobot\.com/captcha/\S+', message.content)
                if url_match: captcha_url = url_match.group(0)
            
            if captcha_url:
                self.bot.paused = True
                self.bot.throttle_until = time.time() + 3600
                self.bot.log("ALARM", "LINK CAPTCHA DETECTED IN DM!")
                await self.play_beep()
                self._show_desktop_notification("DM Captcha detected!")
                
                sec_cfg = self.bot.config.get("security", {})
                sol_cfg = sec_cfg.get("captcha_solver", {})
                
                autosolved = False
                if sol_cfg.get("enabled", True) and sol_cfg.get("api_key"):
                    self.bot.log("SYS", "Attempting YesCaptcha auto-solve for DM...")
                    autosolved = await self.bot.web_solver.auto_verify()
                    if autosolved:
                        self.bot.log("SUCCESS", "YesCaptcha solved successfully (DM)!")
                        self._show_desktop_notification("YesCaptcha solved successfully!")
                    else:
                        self.bot.log("ERROR", "YesCaptcha auto-solve failed (DM)!")
                        self._show_desktop_notification("YesCaptcha failed! Solve manually.")

                if not autosolved:
                    self._send_webhook("DM CAPTCHA", f"Solve link in DM: {captcha_url}")
                    if sys.platform == "win32" and sec_cfg.get("open_captcha_url_on_pc", False):
                        self.bot.log("SYS", "Opening Captcha in Browser with Auto-Login...")
                        asyncio.create_task(self.bot.web_solver.open_in_browser(captcha_url))

                return
        if str(message.author.id) != self.monitor_id: return
        
        if self.bot.owo_user is None:
            self.bot.owo_user = message.author
        try:
            allowed_channels = [int(ch) for ch in self.bot.channels]
        except:
            allowed_channels = [self.bot.channel_id]
            
        if message.channel.id not in allowed_channels: return
        content = message.content or ""
        embed_text = ""
        if message.embeds:
            parts = []
            for e in message.embeds:
                if e.title: parts.append(e.title)
                if e.description: parts.append(e.description)
                if e.footer and e.footer.text: parts.append(e.footer.text)
            embed_text = " ".join(parts)
        text_to_check = f"{content} {embed_text}"
        is_for_me = self.bot.is_message_for_me(message)
        if not is_for_me: return
        if self._contains_keyword(text_to_check, self.ban_keywords):
            self.bot.log("ALARM", "BAN DETECTED!")
            await self._trigger_pause_with_lag(message.channel, "BAN DETECTED", f"Message:\n{content}")
            return
        warning_match = self.warning_pattern.search(text_to_check)
        if warning_match:
            current_warning = int(warning_match.group(1))
            max_warnings = int(warning_match.group(2))
            normalized = self._normalize(text_to_check)
            if any(kw in normalized for kw in ["pleasecomplete", "captcha", "verify", "human"]):
                self.bot.stats['last_captcha_msg'] = text_to_check[:200]
                self.bot.log("ALARM", f"CAPTCHA WARNING DETECTED ({current_warning}/{max_warnings})!")
                
                await self._trigger_pause_with_lag(message.channel, "CAPTCHA WARNING", f"Warning {current_warning}/{max_warnings}\nMessage:\n{content}")
                return
        has_image = len(message.attachments) > 0
        image_captcha_hit = self._contains_keyword(text_to_check, self.image_captcha_keywords)
        if has_image and image_captcha_hit:
            self.bot.stats['last_captcha_msg'] = text_to_check[:200]
            self.bot.log("ALARM", "IMAGE CAPTCHA DETECTED! Warning triggered.")
            
            img_urls = "\n".join([att.url for att in message.attachments])
            await self._trigger_pause_with_lag(message.channel, "IMAGE CAPTCHA DETECTED", f"Message:\n{content}\n\nImages:\n{img_urls}")
            return
        captcha_keywords_hit = self._contains_keyword(text_to_check, self.captcha_keywords)
        captcha_url = self._get_captcha_url(message)
        
        if not captcha_url:
            url_match = re.search(r'https?://owobot\.com/captcha/\S+', text_to_check)
            if url_match:
                captcha_url = url_match.group(0)
        
        if captcha_url or captcha_keywords_hit:
            self.bot.stats['last_captcha_msg'] = text_to_check[:200]
            self.bot.log("ALARM", "CAPTCHA DETECTED! Waiting for human notice time...")
            
            # Phase 11: Differentiated notice times
            # Website captchas (faster, urgent) vs DM captchas (slower)
            if captcha_url:
                notice_delay = random.uniform(5.0, 12.0)
            else:
                notice_delay = random.uniform(15.0, 30.0)
            
            self.bot.log("STEALTH", f"Waiting for human notice time ({round(notice_delay, 1)}s)...")
            
            # Phase 30: Reaction Lag & Stray Commands
            # Allow a small window for strays before full lock
            await self._trigger_pause_with_lag(message.channel, "CAPTCHA DETECTED", f"Captcha Link: {captcha_url or 'Embedded'}", is_captcha=True)

            await asyncio.sleep(notice_delay)
            
            await self.play_beep()
            self._show_desktop_notification("Captcha detected!")
            
            sec_cfg = self.bot.config.get("security", {})
            sol_cfg = sec_cfg.get("captcha_solver", {})
            
            autosolved = False
            if sol_cfg.get("enabled", True) and sol_cfg.get("api_key"):
                self.bot.log("SYS", "Attempting YesCaptcha auto-solve...")
                autosolved = await self.bot.web_solver.auto_verify()
                if autosolved:
                    self.bot.log("SUCCESS", "YesCaptcha solved successfully!")
                    self._show_desktop_notification("YesCaptcha solved successfully!")
                else:
                    self.bot.log("ERROR", "YesCaptcha auto-solve failed!")
                    self._show_desktop_notification("YesCaptcha failed! Solve manually.")

            if not autosolved:
                solve_link = captcha_url or "https://owobot.com/captcha"
                self._send_webhook("CAPTCHA DETECTED", f"Solve: {solve_link}")
                if sys.platform == "win32" and sec_cfg.get("open_captcha_url_on_pc", False):
                    self.bot.log("SYS", "Opening Captcha in Browser with Auto-Login...")
                    asyncio.create_task(self.bot.web_solver.open_in_browser(captcha_url))

            return

    async def _trigger_pause_with_lag(self, channel, title, webhook_msg, is_captcha=False):
        # Phase 30: Reaction Lag Simulation
        # Instead of pausing instantly, we wait 2-5 seconds.
        # This allows any "in-progress" typing to finish organically.
        reaction_lag = random.uniform(2.0, 5.0)
        self.bot.log("STEALTH", f"Security: Human notice lag (Simulating {round(reaction_lag, 1)}s delay before panic stop).")
        
        await asyncio.sleep(reaction_lag)
        
        # Phase 30: Accidental Stray Send (15% chance)
        if random.random() < 0.15:
             stray_cmd = random.choice(["owo h", "owo", "owo b"])
             self.bot.log("STEALTH", f"Stray Command: User accidentally sent '{stray_cmd}' before realizing the alert.")
             await self.bot.neura_enqueue(stray_cmd, priority=1)
             await asyncio.sleep(1.5)

        # Phase 28: Ghost Confusion Typing (2% chance)
        if random.random() < 0.02:
             async with channel.typing():
                  self.bot.log("STEALTH", "Ghost Confusion: Human started typing a question, then stopped.")
                  await asyncio.sleep(random.uniform(2.0, 4.0))

        # Full Lock
        self.bot.paused = True
        self.bot.throttle_until = time.time() + 3600
        await self.play_beep()
        self._show_desktop_notification(f"Security Alert: {title}")
        self._send_webhook(title, webhook_msg)

async def setup(bot):
    await bot.add_cog(Security(bot))
