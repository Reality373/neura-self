import asyncio
import random
import time

cmd_counter_global = 0

async def evaluate_curiosity_trigger(bot, stealth_cfg):
    global cmd_counter_global
    
    cur_cfg = stealth_cfg.get('curiosity', {})
    if not cur_cfg.get('enabled', False):
        return False
        
    curiosity_cmds = cur_cfg.get('commands', ["owo cash", "owo inv", "owo zoo", "owo profile"])
    trigger_min = cur_cfg.get('trigger_min', 20)
    trigger_max = cur_cfg.get('trigger_max', 50)
    
    if curiosity_cmds:
        cmd_counter_global += 1
        if cmd_counter_global > random.randint(trigger_min, trigger_max):
            curiosity_cmd = random.choice(curiosity_cmds)
            bot.log("STEALTH", f"Curiosity triggered: Checking {curiosity_cmd}")
            await bot._send_safe(curiosity_cmd, skip_typing=False)
            bot.last_sent_time = time.time()
            cmd_counter_global = 0
            await asyncio.sleep(random.uniform(2.0, 5.0))
            return True
            
    return False
