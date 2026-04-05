# 6. Dashboard and Data Flow

This final chapter explains the "Bridge" between the Discord Bot's internal state and the interactive Web Dashboard. Understanding this flow is critical for anyone wanting to expand the UI or debug connectivity issues.

## The Async-Sync Bridge

The most complex part of NeuraSelf's architecture is that it runs two entirely different types of software in the same process:
1. **The Discord Bot (Asynchronous):** Uses `asyncio` to handle high-speed WebSocket events.
2. **The Dashboard (Synchronous-ish):** Uses `Flask`, which is traditionally a blocking, thread-based web framework.

### Why not one or the other?
If we ran the dashboard inside the Discord loop, a slow page load would literally "freeze" your bot, causing it to miss captchas or disconnect from Discord. Instead, NeuraSelf uses **Multithreading**.

- The `main.py` script starts the Discord bots in the main event loop.
- It then spawns a separate, background thread specifically for the Flask server.
- These two worlds communicate via the shared memory in `core/state.py`.

## Data Communication (`REST API`)

The Dashboard does not use WebSockets to update stats (to save battery on mobile devices). Instead, it uses a high-frequency **REST Polling** mechanism.

### 1. The Backend (`app.py`)
Flask exposes several "End points" that act as data windows:
- `/api/stats?id=ACCOUNT_ID`: Returns a massive JSON object containing hunts, battles, cash, and stealth metrics.
  - **Aggregation:** Since every account now has its own `stats_{uid}.json` file in the `data/stats/` directory to prevent data corruption, the Flask backend dynamically scans this folder on every request. This ensures total "Zero Collision" safety while still showing you every single account's data in the unified dashboard interface.
- `/api/settings`: Handles the GET (loading) and POST (saving) of your `settings.json` file.
- `/api/logs`: Streams the last 200 lines of terminal output.

### 2. The Frontend (`script.js`)
The browser runs a `setInterval` loop (usually every 1-2 seconds).
1. It pings `/api/stats`.
2. It receives the JSON payload.
3. It uses Vanilla Javascript (`document.getElementById().innerText`) to surgically update only the numbers on the screen.

* **Alternative:** `React` or `Vue.js`.
* **Why we use Vanilla JS:** High-performance frameworks like React require a complicated "Build step" (npm install, webpack, etc). Since NeuraSelf is designed for Termux users, we use raw Javascript that the browser understands natively. This ensures the dashboard is lightning fast even on 5-year-old budget Android phones.

## Real-Time Configuration Updates

When you click "Save Changes" on the dashboard:
1. The browser sends the entire new configuration object to `/api/settings` via a `POST` request.
2. `app.py` writes this immediately to the user's `settings_ID.json` file on the disk.
3. **The Hot-Reload:** Every Cog in the Discord bot (like `Hunting` or `Gambling`) re-reads its local configuration snippet *every single loop*. 

This means you can change your gambling range or toggle off hunting on the dashboard, hit save, and the bot will adapt to the new rules **instantly** without needing to restart the script!

## Final Summary
NeuraSelf is a symphony of separate modules—Security, Stealth, Economy, and UI—all synchronized through a central `state.py` heart. By isolating these concerns, the bot remains stable, modular, and extremely difficult for automated systems to detect.
