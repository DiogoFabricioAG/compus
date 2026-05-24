from textual.screen import ModalScreen
from textual.widgets import Select, Input, Button, Label, Static
from textual.containers import Vertical, Horizontal, Grid
from textual.app import ComposeResult
from textual.reactive import reactive

COMMIT_TYPES = {
    "feat": "A new feature (e.g., introducing a new button or layout)",
    "fix": "A bug fix (e.g., fixing a crash on start)",
    "docs": "Documentation only changes (e.g., updating README.md)",
    "style": "Format changes that do not affect the code meaning (e.g., spacing, semi-colons)",
    "refactor": "A code change that neither fixes a bug nor adds a feature (e.g., cleanup)",
    "perf": "A code change that improves performance",
    "test": "Adding missing tests or correcting existing tests",
    "build": "Changes that affect the build system or external dependencies",
    "ci": "Changes to CI configuration files and scripts",
    "chore": "Other changes that don't modify src or test files"
}

class CommitModal(ModalScreen[tuple[str, str] | None]):
    """Modal for creating a standardized conventional commit."""
    
    def compose(self) -> ComposeResult:
        options = [(f"{k} - {v[:35]}...", k) for k, v in COMMIT_TYPES.items()]
        
        yield Vertical(
            Label("💬 Create Standardized Commit", id="modal-title"),
            Label("Select Commit Type:"),
            Select(options, value="feat", id="commit-type-select"),
            Label(COMMIT_TYPES["feat"], id="type-description"),
            Label("Commit Message:"),
            Input(placeholder="Type your commit message (PALABRAS)...", id="commit-message-input"),
            Horizontal(
                Button("Commit", variant="primary", id="btn-commit"),
                Button("Cancel", variant="error", id="btn-cancel"),
                id="modal-buttons"
            ),
            id="modal-container"
        )

    def on_mount(self) -> None:
        self.query_one("#commit-message-input").focus()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value and event.value in COMMIT_TYPES:
            self.query_one("#type-description").update(COMMIT_TYPES[event.value])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-commit":
            commit_type = self.query_one("#commit-type-select").value
            message = self.query_one("#commit-message-input").value.strip()
            if not message:
                self.query_one("#commit-message-input").placeholder = "⚠️ Message cannot be empty!"
                return
            self.dismiss((commit_type, message))
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "commit-message-input":
            self.query_one("#btn-commit").press()


class ConfirmModal(ModalScreen[bool]):
    """Simple confirmation dialog."""
    
    def __init__(self, message: str, title: str = "Confirm Action"):
        super().__init__()
        self.message = message
        self.title = title

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"❓ {self.title}", id="modal-title"),
            Label(self.message, id="modal-message"),
            Horizontal(
                Button("Yes, Proceed", variant="success", id="btn-yes"),
                Button("Cancel", variant="error", id="btn-no"),
                id="modal-buttons"
            ),
            id="modal-container"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-yes":
            self.dismiss(True)
        else:
            self.dismiss(False)


class BranchModal(ModalScreen[tuple[str, str, str] | None]):
    """Modal to switch or create branches. Returns (action, branch_name, extra)."""
    
    def __init__(self, current_branch: str, branches: list[str]):
        super().__init__()
        self.current_branch = current_branch
        self.branches = branches

    def compose(self) -> ComposeResult:
        options = [(b, b) for b in self.branches]
        
        yield Vertical(
            Label("🌿 Branch Management", id="modal-title"),
            Label(f"Current active branch: {self.current_branch}"),
            Label("Switch to existing branch:"),
            Select(options, value=self.current_branch if self.current_branch in self.branches else None, id="branch-select"),
            Label("Or create a new branch:"),
            Input(placeholder="Type new branch name...", id="new-branch-input"),
            Horizontal(
                Button("Checkout Selected", variant="primary", id="btn-checkout"),
                Button("Create & Checkout", variant="success", id="btn-create"),
                Button("Cancel", variant="error", id="btn-cancel"),
                id="modal-buttons-three"
            ),
            id="modal-container-large"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-checkout":
            selected = self.query_one("#branch-select").value
            if selected:
                self.dismiss(("checkout", selected, ""))
            else:
                self.dismiss(None)
        elif event.button.id == "btn-create":
            new_branch = self.query_one("#new-branch-input").value.strip()
            if not new_branch:
                self.query_one("#new-branch-input").placeholder = "⚠️ Please specify a branch name!"
                return
            self.dismiss(("create", new_branch, ""))
        else:
            self.dismiss(None)


class StashModal(ModalScreen[str | None]):
    """Modal for git stash save message."""
    
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("📦 Stash Current Changes", id="modal-title"),
            Label("Optional Stash Message:"),
            Input(placeholder="Type an optional message for this stash...", id="stash-message-input"),
            Horizontal(
                Button("Stash Changes", variant="primary", id="btn-stash"),
                Button("Cancel", variant="error", id="btn-cancel"),
                id="modal-buttons"
            ),
            id="modal-container"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-stash":
            msg = self.query_one("#stash-message-input").value.strip()
            self.dismiss(msg)
        else:
            self.dismiss(None)


class MergeModal(ModalScreen[str | None]):
    """Modal to select branch to merge into current."""
    
    def __init__(self, current_branch: str, branches: list[str]):
        super().__init__()
        self.current_branch = current_branch
        self.branches = [b for b in branches if b != current_branch]

    def compose(self) -> ComposeResult:
        options = [(b, b) for b in self.branches]
        
        yield Vertical(
            Label("🔀 Merge Branches", id="modal-title"),
            Label(f"Active branch: {self.current_branch}"),
            Label("Select branch to merge INTO current:"),
            Select(options, placeholder="Select a branch...", id="merge-branch-select"),
            Horizontal(
                Button("Merge Branch", variant="warning", id="btn-merge"),
                Button("Cancel", variant="error", id="btn-cancel"),
                id="modal-buttons"
            ),
            id="modal-container"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-merge":
            selected = self.query_one("#merge-branch-select").value
            if not selected:
                return
            self.dismiss(selected)
        else:
            self.dismiss(None)


class RemoteModal(ModalScreen[str | None]):
    """Modal for configuring the origin remote repository URL."""
    
    def __init__(self, current_url: str = ""):
        super().__init__()
        self.current_url = current_url

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("🌐 Configure GitHub Remote", id="modal-title"),
            Label("GitHub Repository URL or Repo Name (e.g., user/repo):"),
            Input(value=self.current_url, placeholder="e.g. https://github.com/user/repo.git", id="remote-url-input"),
            Label("Tip: Typing 'user/repo' automatically expands to the HTTPS GitHub URL.", id="type-description"),
            Horizontal(
                Button("Save Remote", variant="success", id="btn-save"),
                Button("Cancel", variant="error", id="btn-cancel"),
                id="modal-buttons"
            ),
            id="modal-container-large"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            url = self.query_one("#remote-url-input").value.strip()
            if url and not url.startswith("http") and not url.startswith("git@") and "/" in url:
                url = f"https://github.com/{url}.git"
            self.dismiss(url)
        else:
            self.dismiss(None)
