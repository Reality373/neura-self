import asyncio
import random
from datetime import datetime

is_sleeping_global = False
session_mode_global = 'BINGE'

async def handle_circadian_rhythm(bot, stealth_cfg):
    global is_sleeping_global, session_mode_global
    
    cr_cfg = stealth_cfg.get('circadian_rhythm', {})
    if not cr_cfg.get('enabled', False):
        return
        
    now = datetime.now()
    current_hour = now.hour
    sleep_start = cr_cfg.get('sleep_start', 1)
    sleep_end = cr_cfg.get('sleep_end', 8)
    
    is_sleep_time = False
    if sleep_start <= sleep_end:
        is_sleep_time = sleep_start <= current_hour < sleep_end
    else:
        is_sleep_time = current_hour >= sleep_start or current_hour < sleep_end
    
    if is_sleep_time:
        if not is_sleeping_global:
            bot.log("STEALTH", "Circadian Rhythm: Bot is sleeping for the night.")
            is_sleeping_global = True
            
        while is_sleeping_global:
            now = datetime.now()
            current_hour = now.hour
            is_still_sleep = False
            if sleep_start <= sleep_end:
                is_still_sleep = sleep_start <= current_hour < sleep_end
            else:
                is_still_sleep = current_hour >= sleep_start or current_hour < sleep_end
                
            if not is_still_sleep:
                is_sleeping_global = False
                session_mode_global = random.choices(['BINGE', 'CASUAL'], weights=[0.4, 0.6])[0]
                bot.log("STEALTH", f"Circadian Rhythm: Woke up! Session mode: {session_mode_global}")
                break
            await asyncio.sleep(60)

def get_session_mode():
    global session_mode_global
    return session_mode_global

def set_session_mode(mode):
    global session_mode_global
    session_mode_global = mode
