# 2. Core State & Multi-Account Scaling

This chapter explores how the NeuraSelf core engine orchestrates complex multi-account farm setups and manages its internal memory footprint robustly.

## Multi-Account Invocation

NeuraSelf is designed natively for heavy expansion. You can boot ten independent accounts and they will farm seamlessly without crossing wires.

### Boot Sequence (`main.py` & `bot.py`)
When you launch the app, NeuraSelf iterates through `accounts.json`. For every valid token, it instantiates a completely independent iteration of the `NeuraBot` class. Each `NeuraBot` gets its very own isolated:
- Event listener bindings.
- Connection Gateway.
- Config parser context.

* **The Alternative:** Running 10 entirely different python terminals/scripts (`python main.py --token X`).
* **Why we built the Core Loop:** Running multiple Python contexts creates immense redundant overhead. 10 terminals means loading the `discord.py` engine into your RAM 10 different times. By using `asyncio.gather()`, we launch all bots from a single Python memory space asynchronously. It runs 10x lighter on hardware.

## Memory Management (`state.py`)

When passing data between your Discord Account, the Cogs (e.g., `Gambling`, `Hunting`), and the Web Dashboard, we need a "Global Highway" for information. This is exactly what `core/state.py` is dynamically used for.

### Statelessness vs Stateful Memory
If a bot relies entirely on querying APIs (like constantly pinging Discord to check "What is my username?"), you quickly hit rate limits. 
If a bot saves every single thing to the disk, you experience painful I/O (Input/Output) lag, drastically impacting mobile execution speeds.

NeuraSelf marries the benefits of both using rapid in-memory caching mapping.

```python
# From state.py
account_stats = {}
bot_instances = []
```

Every time an account successfully sends an `owo hunt`, the `response_handler.py` cog intercepts the "success" embed, and silently updates the `account_stats[bot_id]['hunt_count']` integer inside `state.py` literally in-memory.

### Isolated Persistence (Zero Collision)
To ensure NeuraSelf can run for weeks without data corruption, we have transitioned away from a single global `stats.json` file. 

Each bot instance now owns its own dedicated storage file inside the `data/stats/` directory (e.g., `stats_10194...json`). 
- **Why we did it:** In multi-account setups, multiple bots trying to write to one file at the exact same millisecond can cause "File Collisions" or truncated data. By isolating every account into its own JSON, we completely eliminate the need for complex global locks and ensure your farming metrics are never lost, even if one specific account crashes.

Because the Flask server thread imports the exact same `state.py` memory block, the Dashboard gathers these individual files into a unified view for the frontend seamlessly.

---

## The Execution Queue (`neura_enqueue`)

If the bot decides it suddenly needs to Hunt, gamble, and equip a gem at the same time, firing them all identically blocks Discord's rate limits and flags you globally.

All cogs are entirely prohibited from using standard `await channel.send()`. Instead, they use:
`await bot.neura_enqueue("owo hunt", priority=4)`

This funnels all actions into a mathematical Heap Queue inside the bot core. 
- `Priority 1 (Urgent):` CAPTCHAs, Alert fallbacks, Pausing system tasks.
- `Priority 2 (High):` Automated recovery (Low money sell-offs, Inventory setups).
- `Priority 3 (Medium):` Gambling routines, Action commands.
- `Priority 4 (Background Grinding):` Hunting, Battling, Questing.

The Bot pulls from this queue dynamically. It ensures that an urgent "Buy a gem" action jumps right over the standard "owo hunt" command, executing the entire lifecycle seamlessly without violating human limitations.
