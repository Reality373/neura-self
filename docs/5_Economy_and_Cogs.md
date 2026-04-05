# 5. Economy and Logic Cogs

NeuraSelf is uniquely segmented into modular classes we call **Cogs** (A concept derived from `discord.py` architecture). Every action inside the bot—such as gambling, opening boxes, or interacting with quests—is completely structurally isolated in its own file under the `cogs/` directory.

## Mathematical Exploitation (Gambling)

The simplest way to maintain a highly human profile is dropping massive `owo cf` (Coinflip) and `owo slots` commands continuously deeply baked inside your grinding loops.

### The Problem with 50/50 Probabilities
All gambling inside OwO Bot is heavily governed by an impenetrable Server-Side RNG (Random Number Generator). There is zero mathematical algorithmic method to predict "Heads/Tails", meaning over a scale of exactly 1 million rolls, your net profit will naturally trend heavily toward exactly $0 due exclusively to Variance. 

### The Solution: Martingale Progressive Betting
To forcefully skew profits upward without triggering flags, `cogs/gambling.py` uses an adaptation of the Martingale Betting System:
- You dictate a betting range in your dashboard (e.g., $100 -> $5,000).
- The bot exclusively opens at the absolute rock bottom ($100).
- When the bot naturally rolls a statistical loss, it actively modifies its bet state variable, automatically triggering an increase on the next bet (e.g., $300) directly aimed at wiping the previous mathematical deficit.
- Only upon resolving a "Win" does the algorithm forcefully flush back down to the $100 bottom threshold.
- *This forces statistical variance to pay out significantly higher during wins, and keeps losses extremely tightly constrained into micro-increments.*

## Intelligence Engines (Inventory and Quests)

If humans run out of currency inside a game logically, they sell something to keep playing. The `cogs/sell_sac.py` script embodies this entirely dynamically. 

Instead of arbitrarily dumping the user inventory every 5 minutes blindly (which is both highly detectable and often results in selling incredibly rare Mythical items on accident), the Economy Engine integrates completely defensively.

### Bankruptcy Mode
If the Discord embed contains an error like `"You don't have enough cowoncy"`, the event loop violently interrupts the primary queue. 
1. The Bot simulates `Frustration`. It enforces a raw asyncio delay (anywhere from 4s to 9s) effectively mimicking the user staring at their phone screen realizing they just bottomed out their balance.
2. It aggressively injects an `owo sell all` task immediately into `Priority 2`, forcing an immediate wallet dump entirely reactively precisely in time to fund the next queued Coinflip action!

### Smart Questing
Rather than ignoring daily checklists, the `cogs/quest.py` uses Regex scanning (`Regular Expressions`) aggressively on any `owo quest` checklist returned. 

Upon successfully analyzing the text fields:
- If a task reads `Say 'owo' 50 times`, it seamlessly spins up an isolated background loop, drip-feeding casual `owo` string commands organically.
- If a task requires `Use an action command 10 times`, the cog manually sweeps and scrapes the latest 20 message histories of the local channel, isolating completely random external human users that are NOT bots. It then executes targeted actions dynamically (`owo hug @Target`).

**Quest Debouncing:**
To prevent the bot from "spamming" automation tasks (which could happen if multiple users trigger checklist messages), NeuraSelf uses an internal `active_resolutions` tracker. It ensures that a specific quest description is only being automated by exactly one background task at any given time, preventing redundant social pings and looking much more organic.

This approach turns a previously agonizingly manual checklist into an invisible, entirely zero-drag background routine.
