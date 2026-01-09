# 🎬 Kartiseret
### A cinematic data pipeline with attitude

Welcome to **Kartiseret** — a terminal-first, automation-heavy, Rich-powered backend project that scrapes, cleans, deduplicates, enriches, and ships cinema data like it actually means business.

This project doesn’t just *run jobs*.  
It **orchestrates runners**, **tracks execution**, **renders beautiful live UIs**, and **keeps your data sane** while doing it.

If you like:
- clean abstractions  
- aggressive deduping  
- deterministic run IDs  
- and a terminal UI that feels alive  

You’re in the right place. 🍿

---

## ✨ What Kartiseret Does

Kartiseret is a **modular dataflow execution engine** built around cinemas, movies, and showtimes.

It handles:

- 🎥 Cinema scrapers (Selenium-based, battle-tested)
- 🔄 Dataflows that clean, enrich, and migrate data
- 🧠 Central registries for discoverability and orchestration
- 🧵 Threaded + sequential execution
- 📊 Rich terminal UI with progress bars, spinners, timers, and live status
- 🆔 Run ID allocation for traceability
- 🧹 Aggressive deduplication & cleanup
- 🧪 Testing vs Regular execution modes

All without turning your terminal into unreadable soup.

---

## 🧱 Architecture Overview

Kartiseret is intentionally layered.

### 1. Runners
The orchestration layer.

- Decide *what* runs
- Decide *how* it runs (threads vs sequential)
- Delegate rendering to Rich
- Stay intentionally thin

> Runners do orchestration, not logic.

---

### 2. Dataflows
Pure data logic.

- Cleaning
- Deduplication
- Moving rows between tables
- Skipping already-processed records
- Retry-safe execution

Every dataflow is:
- Isolated
- Repeatable
- Safe to re-run

---

### 3. Cinema Scrapers
The gritty stuff.

- Selenium automation
- Cookie banners
- Location pickers
- Dynamic DOMs
- Non-cooperative websites

All scrapers inherit from shared base classes so pain is suffered once.

---

### 4. Rich UI Support
Where the ✨ happens.

- Per-task progress bars
- Colored spinners
- Elapsed vs remaining time
- Thread awareness
- Failure visualization

All UI logic lives here so execution code stays clean.

---

## 🖥️ Terminal UI Philosophy

Kartiseret uses **Rich** correctly:

- Alternate screen buffer for menus
- One final clean summary on exit
- No flickering
- No duplicated logs
- No lost scrollback

You’ll see:
- Live progress bars per task
- Pink spinners while pending
- Thread counts
- Precise timings
- Clear failure states

It feels closer to a build system than a script.

---

## 🧪 Execution Modes

Kartiseret supports multiple modes:

### Testing Mode
- Smaller batches
- Faster iteration
- Safer experimentation

### Regular Mode
- Full datasets
- Real tables
- Real consequences

Modes affect:
- Which tables are used
- How much data is processed
- Visual labeling in the UI

---

## 🆔 Run IDs & Traceability

Every execution gets a **unique run ID**.

Why this matters:
- Logs are attributable
- Database writes are traceable
- Parallel runs don’t collide
- Debugging becomes survivable

Run IDs are allocated once and propagated everywhere.

---

## 🧹 Deduplication Strategy

Kartiseret is paranoid about data integrity.

It:
- Dedupes before inserts
- Dedupes before deletes
- Chunks large operations
- Refreshes tables when required
- Skips already-seen rows intelligently

The goal is **idempotent execution**.

> Running the same thing twice should not ruin your day.

---

## 🧠 Design Principles

This project follows a few non-negotiables:

- Separation of concerns
- No UI logic in execution code
- No execution logic in UI code
- Explicit over implicit
- Failures should be visible
- Terminal UX matters

---

## 🚀 How It Runs

At the top level, execution follows a clean flow:

1. Environment loads
2. Logging initializes
3. Run ID is allocated
4. Mode is selected
5. Runners execute
6. Rich UI renders live progress
7. One final clean summary is printed

No magic. No spaghetti.

---

## 🎯 Who This Is For

Kartiseret is for developers who:

- Care about maintainable automation
- Want terminal tools that feel professional
- Are tired of unreadable logs
- Value deterministic data pipelines
- Like their code structured and intentional

---

## 🎬 Final Words

Kartiseret isn’t just scraping cinema data.  
It’s a **framework for running complex jobs without losing control**.

If something breaks, you’ll know where.  
If something fails, you’ll see it.  
If something runs, it’ll look good doing it.

Enjoy the show. 🍿
