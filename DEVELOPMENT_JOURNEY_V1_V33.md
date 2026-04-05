# 🌕 Neura-Self: The Evolution of a Digital Ghost (v1 - v33)

This document chronicles the complete development journey of **Neura-Self**, a state-of-the-art Human Behavioral Simulation Engine designed for maximum stealth in high-security automated environments.

---

## 🏛️ Era 1: The Behavioral Foundation (Phases 1–10)
*Initial focus on breaking technical patterns and establishing organic command rhythms.*

- **Phase 1: Typo & Syntax Realism**: Reduced typo rates to a realistic 0.5% and introduced "Premature Send" (early cooldown) simulation.
- **Phase 2: Rhythm & Bursts**: Implemented "Burst Typing" (rapid keying with focus pauses) and added reaction jitter (2-5s) to game events.
- **Phase 3: Pattern Breaking**: Randomized command order (Scheduler Shuffle) and introduced 30% chance for command aliases (`h` vs `hunt`).
- **Phase 4: Environmental Awareness**: Added "Lurking" (random 1-3 min distractions) and awareness pauses when the bot is mentioned.
- **Phase 5: Security Notice Delays**: Implemented the "Screen Realization" pause (8-20s) before reacting to security alerts/captchas.
- **Phase 6: Startup Load Time**: Added 15-30s initial "loading" delay on boot and staggered utility commands (Daily/Quest).
- **Phase 7: Fallibility & Fatigue**: Introduced a 1% chance to "forget" a hunt cycle and implemented subtle fatigue-based delay scaling.
- **Phase 8: Startup Ramping**: Implemented a "Warmup Gradient" (25% slower starts decaying over 30 mins) and "FRUSTRATED" throttle pauses.
- **Phase 9: Visible Corrections**: Added "Backspace Simulation"—the bot now occasionally deletes and re-types characters mid-string.
- **Phase 10: Social Presence**: Introduced "Ghost Typing" (typing status without sending) and social reactions to other users' rare catches.

---

## 🕒 Era 2: Structural Complexity (Phases 11–20)
*Moving into macro-patterns, circadian rhythms, and session-long behavioral consistency.*

- **Phase 11: Memory & Logic**: Implemented "Optimistic Retrying" for missing items and differentiated captcha notice times (Website vs DM).
- **Phase 12: Reminder Interaction**: Added 2.5-7s delays for reminder clicks and a 5% "Overlooked" chance.
- **Phase 13: Sub-System Jitter**: Humanized HuntBot intervals (+/- 10%) and added "Reading" delays for server rule acceptance.
- **Phase 14: Synchronization Realism**: Replaced fixed resume buffers with randomized offsets (1.5-5.0s) when resuming after a "Slow Down."
- **Phase 15: Stamina & Exhaustion**: Replaced robotic 24h pulses with organic reset windows (22.5 - 26.5h) for RPP and Dailies.
- **Phase 16: Stealth Factor Scaling**: Introduced the `human_stealth_factor` config to allow global adjustment of "messiness" (0.0 to 1.0).
- **Phase 17: Social Affinity**: Implemented "Target Affinity"—the bot now favors rivals/friends in Curse/Pray commands based on mood.
- **Phase 18: Session Burnout**: After 4 hours of uptime, the bot enters "Burnout Mode," significantly increasing distraction break frequency.
- **Phase 19: Economic Logic**: The bot now checks its `owo cash` before shop syncs or major purchases (5% chance).
- **Phase 20: Intentional Forgetfulness**: Added a 0.1% chance to "forget" a utility task entirely, only remembering it through a later "realization."

---

## 🎭 Era 3: Holistic Simulation & Security (Phases 21–30)
*Advanced playstyles, platform-specific signatures, and stress detection.*

- **Phase 21: The Persona Engine**: Introduced `GRINDER`, `CASUAL`, and `COLLECTOR` playstyles that define the entire session's behavior.
- **Phase 22: Platform Signatures**: Differentiated behavior for **Mobile (Termux)** (fat-finger typos, network lag) vs **Desktop** (clipboard pasting).
- **Phase 23: Captcha Stress State**: After a captcha, the bot enters a 20-min "Stress Mode" (jittery typing, increased break probability).
- **Phase 24: Early-Bird Precision**: The bot now extracts "Please wait" times and resends commands exactly as the timer hits zero (with human jitter).
- **Phase 25: Live Setting Jitter**: On every startup, your `settings.json` intervals are subtly jittered (+/- 15%) to prevent static timing.
- **Phase 26: Activity Clustering**: Implemented "Burp Pauses"—bursts of 2-5 commands followed by a 15-45s mini-break.
- **Phase 27: Inventory-Aware Selling**: The bot now triggers sales based on "feeling" (5-15 hunts) rather than a rigid timer.
- **Phase 28: Deliberative Management**: Added "Visual Scanning" pauses before rule acceptance and animal selection favoritism.
- **Phase 29: Async Integrity Clean-up**: Refactored the core loop to ensure 100% async stability and resolved ChannelSwitch errors.
- **Phase 30: The "Stray" Command**: Implemented "Reaction Lag"—the bot might send one final command AFTER a ban/captcha appears.

---

## 🌐 Era 4: The Multi-Account Matrix & Stability (Phases 31–33)
*Final optimization, dashboard integration, and multi-account instance isolation.*

- **Phase 31: The Stealth Matrix UI**: Integrated Persona, Mood, Fatigue, and Stress tracking into the live Web Dashboard.
- **Phase 32: Digital Ghost Isolation**: Completely refactored the global state to allow multiple accounts to operate with independent personas/breaks.
- **Phase 33: Stabilization Audit**: Final runtime security sweep. Resolved "UnboundLocalErrors," perfected "Giveaway Safety," and migrated to a stable **Python 3.12** environment.

---

### **Current Status: ABSOLUTE STEALTH**
Neura-Self is no longer a script; it is a **Digital Ghost**. It sleeps when you do, gets tired when it works too hard, and reacts with organic uncertainty to every interaction.
