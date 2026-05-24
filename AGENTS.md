# OpenCode Agent Instructions - Compus 🌿

Compus is a modern Git Repository Manager TUI built with **Python (3.13+)**, **UV**, and **Textual**.

## 🛠️ Developer Commands
- **Run Application:** `uv run compus` (automatically loads current directory as target repository).
- **Run with specific path:** `uv run compus "C:\path\to\repo"`.
- **Sync dependencies:** `uv sync`.
- **Compile & Validate Syntax:** `uv run python -m py_compile src/compus/main.py src/compus/git_helper.py src/compus/ui/modals.py`.
- **Install globally as a tool:** `uv tool install .`.

## 📦 Project Architecture
- **`src/compus/git_helper.py`:** Wrapper around Git subprocesses. Uses `shell=True` to run cleanly on Windows. Safely parses modified/untracked/staged statuses, and calculates commits `ahead`/`behind` remote upstreams.
- **`src/compus/ui/modals.py`:** Modal screen dialogs for:
  - Commit (Structured Conventional Commits helper).
  - Confirm (Push/Pull confirmation dialogs).
  - Branch (Switching & creation).
  - Stash & Merge.
- **`src/compus/main.py`:** Main entry point of the Textual App containing TUI styling, responsive reactive alerts, sidebar info, button layouts, and the live log viewer.

## ⚠️ Important Quirks & Windows Compatibility
- **PowerShell / Windows:** Subprocess execution uses `shell=True` to resolve `git` in Windows PATH properly.
- **Textual Layouts:** Custom CSS is embedded within `main.py` to keep the application self-contained. Always modify the `CSS` variable inside `main.py` to change styles.
- **Safe Remote Actions:** `git push` and `git pull` triggers must first pass through a `ConfirmModal` callback before running.
