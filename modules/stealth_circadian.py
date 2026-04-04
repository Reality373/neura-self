import asyncio
import random
from datetime import datetime

is_sleeping_global = False
session_mode_global = 'BINGE'
session_persona_global = 'GRINDER' # Phase 21: Personas

async def handle_circadian_rhythm(bot, stealth_cfg):
    global is_sleeping_global, session_mode_global
    
    cr_cfg = stealth_cfg.get('circadian_rhythm', {})
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
        if not is_sleeping_global:
            bot.log("STEALTH", "Circadian Rhythm: Bot is sleeping for the night.")
            is_sleeping_global = True
            
        while is_sleeping_global:
            now = datetime.now()
            current_hour = now.hour + (now.minute / 60.0)
            is_still_sleep = False
            if sleep_start <= sleep_end:
                is_still_sleep = sleep_start <= current_hour < sleep_end
            else:
                is_still_sleep = current_hour >= sleep_start or current_hour < sleep_end
                
            if not is_still_sleep:
                bot.circadian_jitter = random.uniform(-0.5, 0.5)
                is_sleeping_global = False
                session_mode_global = random.choices(['BINGE', 'CASUAL'], weights=[0.4, 0.6])[0]
                
                # Phase 25: Persona Override Support
                force_persona = stealth_cfg.get('force_persona', 'auto').upper()
                if force_persona != 'AUTO':
                     session_persona_global = force_persona
                else: 
                     # Phase 21: Persona weighted roll based on time of day
                     current_hour_int = datetime.now().hour
                     if 8 <= current_hour_int < 12: # Morning
                         session_persona_global = random.choices(['GRINDER', 'CASUAL', 'COLLECTOR'], weights=[20, 60, 20])[0]
                     elif 12 <= current_hour_int < 18: # Afternoon
                         session_persona_global = random.choices(['GRINDER', 'CASUAL', 'COLLECTOR'], weights=[50, 30, 20])[0]
                     elif 18 <= current_hour_int < 24: # Evening
                         session_persona_global = random.choices(['GRINDER', 'CASUAL', 'COLLECTOR'], weights=[70, 20, 10])[0]
                     else: # Late Night
                         session_persona_global = random.choices(['GRINDER', 'CASUAL', 'COLLECTOR'], weights=[80, 10, 10])[0]
                
                bot.log("STEALTH", f"Circadian Rhythm: Woke up! Mode: {session_mode_global}, Persona: {session_persona_global}")
                break
            await asyncio.sleep(60)

def get_session_mode():
    global session_mode_global
    return session_mode_global

def set_session_mode(mode):
    global session_mode_global
    session_mode_global = mode

def get_session_persona():
    global session_persona_global
    return session_persona_global

def set_session_persona(persona):
    global session_persona_global
    session_persona_global = persona
