import asyncio
import random
import time

async def evaluate_curiosity_trigger(bot, stealth_cfg):
    cur_cfg = stealth_cfg.get('curiosity', {})
    if not cur_cfg.get('enabled', False):
        return False
        
    curiosity_cmds = cur_cfg.get('commands', ["owo cash", "owo inv", "owo zoo", "owo profile"])
    trigger_min = cur_cfg.get('trigger_min', 100)
    trigger_max = cur_cfg.get('trigger_max', 250)
    
    if not hasattr(bot, 'cmd_counter'):
        bot.cmd_counter = 0

    if curiosity_cmds:
        bot.cmd_counter += 1
        if bot.cmd_counter > random.randint(trigger_min, trigger_max):
            curiosity_cmd = random.choice(curiosity_cmds)
            bot.log("STEALTH", f"Curiosity triggered: Checking {curiosity_cmd}")
            await bot._send_safe(curiosity_cmd, skip_typing=False)
            bot.last_sent_time = time.time()
            bot.cmd_counter = 0

            await asyncio.sleep(random.uniform(2.0, 5.0))
            return True
            
    return False
