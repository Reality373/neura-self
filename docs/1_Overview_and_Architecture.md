# 1. Overview and Architecture

Welcome to the **NeuraSelf** Core Documentation. This guide is built to structurally dissect how the NeuraSelf farming engine operates under the hood. Whether you are looking to debug the bot, learn advanced Python automation architectural patterns, or write your own cogs, this document serves as your definitive starting point.

## What is NeuraSelf?

NeuraSelf is a fully autonomous, highly-stealthy Discord Self-Bot farm manager built explicitly to interact with `OwO Bot`. Unlike traditional bots that act as utility plugins for a server, NeuraSelf impersonates an actual human user. It uses advanced behavioral simulation to read events, think about responses, take breaks, and send commands exactly like a regular Discord player would.

---

## The Technology Stack

### 1. Framework: `discord.py-self`
To write automation for Discord user accounts, we use a specifically modified fork of the Discord API wrapper called `discord.py-self`. 

* **The Alternative:** `requests` (Raw HTTP spamming). 
* **Why we didn't use it:** Sending raw HTTP POST requests to discord's message endpoint is wildly fast, but it doesn't open a persistent WebSocket. If you aren't connected to the WebSocket, Discord flags your account immediately because "real users" use apps that establish WebSocket gateways to receive live typing/message events. `discord.py-self` seamlessly handles the background WebSocket heartbeat required to look like an official client session.

### 2. Database Structure: Dynamic JSON
All configuration grids and analytics states in NeuraSelf are stored in standard `.json` files (`settings.json`, `accounts.json`).

* **The Alternative:** `SQLite` or `PostgreSQL` (Relational SQL databases).
* **Why we use JSON:** JSON is incredibly lightweight, instantly readable, and entirely file-based. NeuraSelf is heavily used by mobile script users (using environments like Termux on Android). Forcing a mobile user to install SQL bindings or run a database daemon is completely overkill and leads to immense compatibility issues. With JSON, the deployment is essentially "drag-and-drop," and any user can manually adjust their settings using a basic text editor.

### 3. Dashboard WebServer: `Flask`
We use Flask to serve the interactive configuration UI. 

* **The Alternative:** `FastAPI` (Modern async frameworks) or local `Tkinter/PyQt` interfaces.
* **Why we use Flask:** Python natively operates in a synchronous blocking manner. To avoid the dashboard server "blocking" the Discord bot's operations, we aggressively multi-thread. Flask is historically easy to bundle and runs brilliantly on low-resource mobile hardware. We run Flask in a completely isolated thread (`app.run(threaded=True)`). This isolation guarantees that clicking "Save Settings" on your phone's browser will never interrupt a critical Coinflip logic gate executing on the separate Discord thread! 

---

## Architectural Flow

To ensure the bot never trips over itself, everything is designed heavily asynchronously (`asyncio`). 
When a Discord user receives a message, here is what exactly happens internally:

1. **The Gateway (Event Loop):** Discord sends a JSON packet over the WebSocket. The `discord.py` engine translates this payload.
2. **The Listener:** Our `on_message` listeners (inside our `cogs/` modules) catch the message. 
3. **The Brain (`bot.neura_enqueue`):** Instead of firing a response back immediately (which looks highly automated), the Cogs simply hand the requested command (like `owo hunt`) into NeuraSelf's **Priority Execution Server** inside `bot.py`.
4. **The Actor:** The execution server waits dynamically based on human typing speeds (calculated via WPM), locks the channel, creates a native `typing()` visual indicator, and finally dispatches the command.

This architecture specifically decouples **Decision Making** from **Action Execution**, which is the fundamental secret sauce of mimicking humanity.

### 4. Bot Lifecycle & Cleanup
To ensure NeuraSelf can run for weeks uninterrupted, it implements a strict **Resource Cleanup** policy. When a bot instance is stopped or the script is terminated, the engine triggers a `cleanup()` sequence. This forcefully closes active `aiohttp` network sessions and ensures all pending stats are flushed to their respective files, preventing memory leaks and file descriptor exhaustion on mobile devices.
