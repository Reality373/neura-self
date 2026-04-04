import asyncio
import random

async def apply_post_captcha_fatigue(bot, stealth_cfg):
    fatigue_cfg = stealth_cfg.get('post_captcha_fatigue', {})
    if not fatigue_cfg.get('enabled', False):
        return

    delay_min = fatigue_cfg.get('delay_min', 30.0)
    delay_max = fatigue_cfg.get('delay_max', 120.0)
    
    fatigue_delay = random.uniform(delay_min, delay_max)
    bot.log("STEALTH", f"Fatigue: Bot taking a breather for {int(fatigue_delay)} seconds.")
    await asyncio.sleep(fatigue_delay)
