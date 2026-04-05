# 3. Stealth and Humanity Engine

The single most defining feature of the NeuraSelf farming architecture is its ability to bypass advanced server-side automated-activity detectors. 

## The Philosophy of Simulation
Most generic OwO bots operate on static loop timers (Cron timers). If you tell them to hunt every 15 seconds, they will send an API request exactly at the 15.000s mark, flawlessly, 10,000 times a day.

To server moderators and Discord trust-and-safety algorithms, zero-variance perfection is mechanically identical to cheating! A real human takes micro-pauses to scratch their nose, reads the chat periodically, and gets tired dynamically as the day progresses. NeuraSelf exists solely to mathematically simulate this exact human inefficiency.

## Typing Simulation (`typing` configuration)

When NeuraSelf generates an event from its queue, it doesn't instantly instantly drop `owo hunt` into the channel.

Instead, the `stealth.typing` module activates.
1. **Speed Analysis:** It estimates a Base Words-Per-Minute (WPM) variable.
2. **Channel Hooking:** It triggers Discord's official `async with channel.typing():` socket event, making the familiar "Neura is typing..." tag appear locally to anyone watching the channel!
3. **Execution Delay:** The framework manually locks the thread (`asyncio.sleep()`) for the exact mathematical amount of microseconds it would take a 60 WPM human to type the specific string length of the command.
4. **Typo Generations:** At a configured chance (e.g., 4%), the bot decides it "fumbled" the keyboard. It will type out the command, add 0.5s of artificial delay to simulate "realizing" the mistake, and then "backspaces" dynamically before firing. 

## Activity Clustering & Breaks

Instead of spreading out commands perfectly linearly, NeuraSelf uses **Activity Clustering**.
This heavily mimics a gamer "Bingeing" commands, resting, and bingeing again.
It is extremely common for NeuraSelf to rapidly fire 4 separate commands back-to-back inside 10 seconds, and then completely drop dead silent for 40 entire seconds to simulate "reading the embeds" or "looking away from the screen."

### Real-Time Fatigue
Inside `modules/stealth_circadian.py`, the `fatigue_simulation` tracks exactly how long the specific Discord account token has been logged into the websocket.
As the hours pass without taking a "Human Break", the bot calculates a `fatigue_multiplier`. This heavily punishes the bot's reaction speeds, forcing it to naturally type slower, dither longer between embeds, and increase pause rates entirely dynamically. 

### Circadian Rhythm Sleep
You can easily configure NeuraSelf to force an absolute terminal shutdown of event cycles during specific windows (e.g., `1 AM to 8 AM`).
- **The Alternative:** Pressing "Stop Bot" manually, or using OS-level script terminators.
- **Why we built it internally:** Terminating the bot script forces a full WebSocket disconnect. Doing this predictably at the exact same time every day gives away data. By utilizing Circadian Rhythms inside the bot's code, we inject `daily_jitter_min` variables. Today the bot might forcefully "fall asleep" at `01:14 AM`. Tomorrow it might stay up late until `01:47 AM`. This rolling variance is theoretically impossible to classify defensively.
