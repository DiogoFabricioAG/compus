# Compus 🌿

**Compus** is a modern, fast, and beautiful Terminal User Interface (TUI) for Git and GitHub repository management, powered by **Python**, **UV**, and **Textual**.

Designed specifically for developers who love keyboard-driven flows, Compus turns complex or repetitive git operations into delightful, interactive terminal widgets with real-time status tracking and visual warnings.

---

## ✨ Features

- 🌿 **Current Path Reference:** Automatically opens in your active terminal folder.
- ⚡ **Interactive Shortcuts:** Manage your whole workflow using intuitive single-key hotkeys.
- 💬 **Conventional Commits Dialog:** A structured commit modal allowing you to select types like `feat`, `fix`, `docs`, etc. with live descriptions, automatically building standard conventional commit messages (`feat: message`).
- ⚠️ **Reactive Visual Alerts:** Big status cards that light up or warn you if you have many uncommitted changes or if your local branch is behind the remote upstream (pull recommended).
- 🔒 **Safe Execution Modals:** Confirmation modals before pushing, pulling, or merging to prevent accidental remote or working tree overwrites.
- 📺 **Live Activity Logs:** Bottom console panel printing real-time git execution outputs, errors, and success notifications.

---

## ⌨️ Shortcuts / Keyboard Bindings

| Key | Action | Description |
|---|---|---|
| `C` | **Commit Changes** | Opens the Conventional Commit form |
| `P` | **Git Pull** | Safeguarded remote pull from origin branch |
| `U` | **Git Push** | Safeguarded remote push to origin branch |
| `B` | **Branch Manager** | Select existing branches or create a new branch |
| `S` | **Stash Changes** | Stash your current changes or POP (restore) the latest stash |
| `M` | **Merge Branch** | Select a branch to merge into your active branch |
| `R` | **Refresh Status** | Manually sync status with local repository and remote |
| `Q` | **Quit** | Close Compus safely |

---

## 🚀 How to Run

Compus is managed with **UV**, the ultra-fast Python package and project manager.

### Run in current directory
To start Compus directly in your current folder:
```powershell
uv run compus
```

### Run specifying a path
You can also pass a path as an argument to manage a specific repository:
```powershell
uv run compus "C:\Path\To\Your\Repo"
```

---

## 🛠️ Installation

If you'd like to install Compus globally so that you can run `compus` from any folder on your machine:
```powershell
uv tool install .
```
And then simply run:
```bash
compus
```
