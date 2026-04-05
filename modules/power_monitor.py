import asyncio
import subprocess
import json
import random
import time

async def start_power_monitor(bot):
    """
    Background worker that monitors Android battery status via Termux-API.
    If battery is low and not charging, it pauses the bot to preserve hardware life.
    """
    if not bot.is_mobile:
        return

    bot.log("SYS", "Power Monitor: Started background battery check.")
    
    while bot.active:
        try:
            # Check every 10 minutes to save cpu/battery
            await asyncio.sleep(600) 
            
            # Execute termux-battery-status
            proc = await asyncio.create_subprocess_exec(
                'termux-battery-status',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                data = json.loads(stdout.decode())
                percentage = data.get('percentage', 100)
                status = data.get('status', 'DISCHARGING') # DISCHARGING, CHARGING, FULL, NOT CHARGING
                
                # Logic: If < 15% and not charging -> Deep Sleep
                if percentage < 15 and status != "CHARGING":
                    if not bot.paused:
                        bot.log("ALARM", f"Power Save: Battery low ({percentage}%). Entering Deep Sleep to preserve phone life.")
                        bot.paused = True
                        # Set a very long throttle to prevent accidental resumes
                        bot.throttle_until = time.time() + 3600 
                
                # Logic: If > 20% or charging -> Resume if we were paused for power
                elif (percentage > 20 or status == "CHARGING"):
                    if bot.paused and "Power Save" in state.command_logs[0]['message']:
                         bot.log("SUCCESS", f"Power Restore: Battery healthy ({percentage}% / {status}). Resuming operations.")
                         bot.paused = False
                         bot.throttle_until = 0
            
        except Exception as e:
            # Silently fail or log debug if termux-api isn't installed
            # bot.log("DEBUG", f"Power Monitor Error: {e}")
            pass

def setup_power_monitor(bot):
    asyncio.create_task(start_power_monitor(bot))
