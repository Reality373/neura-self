# 4. Security, Captchas, and Recovery

Automating interaction within strict environments requires a robust defense layer against unexpected interruptions. In the world of `OwO Bot`, the ultimate interruption is the Captcha Challenge. NeuraSelf treats resolving this securely as a absolute highest priority.

## Captcha Detection Engine (`cogs/security.py`)

When the core listener processes any incoming embed, it actively scans message bodies entirely for "suspicious" challenge identifiers. Furthermore, if a moderator visually DMs the account a captcha image, NeuraSelf intercepts the DM payload separately.

**Upon flagging an active captcha, NeuraSelf undergoes the `Full Lock` Phase:**
1. It immediately sets the target account instance to a strict hard-paused state (`self.bot.paused = True`).
2. It forcefully prevents the account queue (`neura_enqueue`) from popping new tasks out to Discord.
3. It intentionally triggers the "Accidental Stray Send" simulator (A 15% probability that the bot sends exactly one extra command to heavily sell the simulation that a human didn't instantly process the panic stop, making the "pause" look completely organically slow).

**Hardened Resumption:**
NeuraSelf doesn't just wait for a manual "Resume" click. It actively listens to your Direct Messages (DMs). When OwO Bot sends the "I have verified that you are human" success message, NeuraSelf intercepts it instantly. It automatically clears the `paused` state, resets all safety throttles, and performs a "Stress Mode" simulation (increased alertness for 20 minutes) to perfectly mimic a human returning to their phone after a scare.

## Hardware Layer Alerts

Most standard scripts attempt to ping you by shooting a message over a Discord Webhook to your main discord account. This is notoriously unreliable because many of us have our phones on DND (Do Not Disturb) or ignore standard Discord pings while out in public.

### The Termux Solution (`termux-api`)
Instead of simply sending webhooks, NeuraSelf interfaces directly with the raw hardware of Android using the `Termux:API`.
- When an alarm is triggered, the Python backend binds natively over to the OS.
- Using `termux-media-player`, the bot pushes the `security_beep.mp3` file across Android's explicit **Media/Music** audio stream. By simply renaming your favorite ringtone track into this file, the alarm is absolutely indistinguishable from a standard incoming phone call, eliminating the awkwardness of an "anime bot alarm" triggering in public spaces.

### Termux Power Save Mode
For mobile-first stability, NeuraSelf includes a background **Power Monitor**. Every 10 minutes, the bot queries `termux-battery-status`. 
- **Deep Sleep:** If your battery drops below **15%** and the phone is not currently charging, NeuraSelf will gracefully pause all farming. This prevents your phone from dying unexpectedly while you are away, which could lead to missed captchas or account flags.
- **Auto-Resume:** The moment you plug your phone in (status: `CHARGING`), the bot detects the power restore and automatically resumes its farming cycle.

## Deep-Linking Captcha Recoveries (`modules/web_solver.py`)

When a user sits manually waiting to resolve an alarm, the workflow typically involves: Hearing alarm -> Opening discord -> Checking which account got flagged -> Clicking the OwO Captcha Link -> Wait, opening browser -> Having to manually type out Discord login credentials to authorize -> Solving -> Switching back.

**NeuraSelf fundamentally destroys this latency workflow by integrating Auto-Login URLs.**
Because NeuraSelf holds your raw Discord User Authentication token dynamically inside its execution scope, it leverages an advanced Discord OAuth endpoint wrapper internally. When an alarm triggers:
1. It uses your token to grab a one-time session URL natively.
2. It pushes a system request via `termux-open-url "{redirect_url}"` to forcefully slide open your phone's default browser on top of your screen automatically.
3. It drops you explicitly on the Captcha puzzle, saving you nearly a consecutive minute of frustrating login routing.

### Third-Party Extensibility
If you absolutely demand total hands-free operation, the `modules/web_solver.py` is pre-integrated and compatible with AI automated-solving modules like `YesCaptcha`. It binds a cloud-computation request, pipes the puzzle array back to the Discord account, automatically authenticates the URL array payloads, and resumes farming—with exactly zero input globally.
