# Neura-Self Configuration Guide

This guide breaks down every parameter inside your `settings.json` file so you can customize Neura-Self perfectly to your exact playstyle. 

To use these settings, rename `config/settings.example.json` to `config/settings.json` and fill in your values.

---

## 1. Core Settings (`"core"`)
These are the fundamental settings required for the bot to run and identify itself.

*   **`prefix`**: The prefix Neura-self will use to dispatch commands. Typically `"owo "`. Leave the trailing space! If you want to use an alias, you can change this to `"alias "`.
*   **`user_id`**: Your Discord Account ID (Right click your profile -> Copy ID).
*   **`monitor_bot_id`**: The ID of the bot you are grinding. (OwO Bot is `408785106942164992`).

---

## 2. Stealth Settings (`"stealth"`)
This block controls all the modular human-like behaviors designed to keep you under the radar.

### Human Breaks (`"human_break"`)
Controls standard, generic activity pausing.
*   **`enabled`**: `true` or `false`.
*   **`duration_min`**: How long the bot pauses for (in minutes) when a break triggers. 
*   **`interval_min`**: The bot will check if it needs a break every X minutes.

### Keystroke Typing (`"typing"`)
Controls how the bot natively mimics raw Discord keystrokes.
*   **`enabled`**: Enable or disable organic typing indicators.
*   **`reaction_min` & `reaction_max`**: Base reaction time (in seconds) the bot waits before starting to type a response.
*   **`mistake_rate`**: The percentage chance (e.g., `5` = 5%) the bot intentionally types an adjacent letter on a QWERTY keyboard.
*   **`lazy_typo_rate`**: The percentage chance (e.g., `2` = 2%) that if the bot makes a mistake, it *doesn't* fix it, and submits the typo raw. 
*   **`extra_delay`**: A flat extra wait time padded to every command send.

### Sleep Schedule (`"circadian_rhythm"`)
Simulates you going to bed at night.
*   **`enabled`**: `true` or `false`.
*   **`sleep_start`**: The hour in 24h format the bot goes to sleep (e.g. `1` = 1:00 AM).
*   **`sleep_end`**: The hour the bot wakes up (e.g. `8` = 8:00 AM).

### Formatting Randomizer (`"syntax_variance"`)
Occasionally alters the command string structurally to throw off algorithmic detection patterns.
*   **`enabled`**: `true` or `false`.
*   **`capitalization_rate`**: The chance (e.g. `15`%) the bot randomly capitalizes a letter like `oWo hunt`.
*   **`space_rate`**: The chance (e.g. `10`%) the bot adds a double space like `owo  hunt`.

### Distraction Module (`"curiosity"`)
Breaks predictable farming sequences by randomly throwing in a dummy command.
*   **`enabled`**: `true` or `false`.
*   **`commands`**: A list of commands the bot can randomly pick from.
*   **`trigger_min` & `trigger_max`**: The command counter range. E.g., if set to 20-50, somewhere between the 20th and 50th message, it will fire a dummy command.

### Post-Captcha Exhaustion (`"post_captcha_fatigue"`)
Simulates the reluctance a human feels directly after dealing with an annoying captcha verification.
*   **`enabled`**: `true` or `false`.
*   **`delay_min` & `delay_max`**: Represents seconds. When a captcha is successfully bypassed, the bot will globally pause for a random duration between these numbers before it resumes grinding.

---

## 3. Command Shortforms & Aliases

You can configure aliases like `owo h` for `owo hunt` using the `shortform.json` file inside the `config/` directory.

**Example `config/shortform.json`:**
```json
{
    "h": "hunt",
    "b": "battle"
}
```
Neura-self will natively intercept strings with these shorthand keys and convert them dynamically in memory while letting the external view on Discord remain minimal.
