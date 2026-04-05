import asyncio
import random
from datetime import datetime

async def handle_circadian_rhythm(bot, stealth_cfg):
    session_cfg = stealth_cfg.get('session', {})
    cr_cfg = session_cfg.get('circadian_rhythm', stealth_cfg.get('circadian_rhythm', {}))
    if not cr_cfg.get('enabled', False):
        return
        
    now = datetime.now()
    current_hour = now.hour + (now.minute / 60.0)
    
    if not hasattr(bot, 'circadian_jitter'):
        bot.circadian_jitter = random.uniform(-0.5, 0.5)
        
    sleep_start = cr_cfg.get('sleep_start', 1) + bot.circadian_jitter
    sleep_end = cr_cfg.get('sleep_end', 8) + bot.circadian_jitter
    
    # normalize bounds if they exceed 24
    sleep_start %= 24
    sleep_end %= 24
    
    is_sleep_time = False
    if sleep_start <= sleep_end:
        is_sleep_time = sleep_start <= current_hour < sleep_end
    else:
        is_sleep_time = current_hour >= sleep_start or current_hour < sleep_end
    
    if is_sleep_time:
        if not bot.is_sleeping:
            bot.log("STEALTH", "Circadian Rhythm: Bot is sleeping for the night.")
            bot.is_sleeping = True
            
        while bot.is_sleeping:
            now = datetime.now()
            current_hour = now.hour + (now.minute / 60.0)
            is_still_sleep = False
            if sleep_start <= sleep_end:
                is_still_sleep = sleep_start <= current_hour < sleep_end
            else:
                is_still_sleep = current_hour >= sleep_start or current_hour < sleep_end
                
            if not is_still_sleep:
                bot.circadian_jitter = random.uniform(-0.5, 0.5)
                bot.is_sleeping = False
                bot.session_mode = random.choices(['BINGE', 'CASUAL'], weights=[0.4, 0.6])[0]
                
                force_persona = session_cfg.get('force_persona', stealth_cfg.get('force_persona', 'auto')).upper()
                if force_persona != 'AUTO':
                     bot.session_persona = force_persona
                else: 
                     current_hour_int = datetime.now().hour
                     if 8 <= current_hour_int < 12: # Morning
                         bot.session_persona = random.choices(['GRINDER', 'CASUAL', 'COLLECTOR'], weights=[20, 60, 20])[0]
                     elif 12 <= current_hour_int < 18: # Afternoon
                         bot.session_persona = random.choices(['GRINDER', 'CASUAL', 'COLLECTOR'], weights=[50, 30, 20])[0]
                     elif 18 <= current_hour_int < 24: # Evening
                         bot.session_persona = random.choices(['GRINDER', 'CASUAL', 'COLLECTOR'], weights=[70, 20, 10])[0]
                     else: # Late Night
                         bot.session_persona = random.choices(['GRINDER', 'CASUAL', 'COLLECTOR'], weights=[80, 10, 10])[0]
                
                bot.log("STEALTH", f"Circadian Rhythm: Woke up! Mode: {bot.session_mode}, Persona: {bot.session_persona}")
                break
            await asyncio.sleep(60)

# Backward Compatibility functions - will return instance state if bot is passed
def get_session_mode(bot=None):
    if bot: return getattr(bot, 'session_mode', 'BINGE')
    return 'BINGE'

def set_session_mode(bot, mode):
    bot.session_mode = mode

def get_session_persona(bot=None):
    if bot: return getattr(bot, 'session_persona', 'GRINDER')
    return 'GRINDER'

def set_session_persona(bot, persona):
    bot.session_persona = persona

