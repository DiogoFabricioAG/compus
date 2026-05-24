import os
import sys
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Button, RichLog, Label, Static
from textual.reactive import reactive
from textual.binding import Binding

from compus.git_helper import GitHelper
from compus.ui.modals import CommitModal, ConfirmModal, BranchModal, StashModal, MergeModal, RemoteModal

# Textual TUI Stylesheet (Fully compliant with Textual CSS parser)
CSS = """
Screen {
    background: #0f1015;
    color: #c9d1d9;
}

Header {
    background: #1f2335;
    color: #ff9e64;
    text-align: center;
    text-style: bold;
    height: 3;
}

Footer {
    background: #1f2335;
    color: #787c99;
}

#layout {
    layout: horizontal;
    padding: 1;
}

#left-sidebar {
    width: 32;
    background: #16161e;
    border: tall #3b4261;
    border-title-color: #7aa2f7;
    padding: 1;
    margin-right: 1;
}

#main-panel {
    width: 1fr;
    layout: vertical;
}

#action-buttons {
    layout: grid;
    grid-size: 4;
    grid-columns: 1fr 1fr 1fr 1fr;
    grid-rows: 3 3;
    grid-gutter: 1;
    height: 7;
    margin-bottom: 1;
}

Button {
    width: 100%;
    height: 100%;
    text-style: bold;
    border: none;
}

#btn-commit { background: #3b4261; color: #ff9e64; }
#btn-pull { background: #223249; color: #7aa2f7; }
#btn-push { background: #1b3a24; color: #73daca; }
#btn-branch { background: #38294a; color: #bb9af7; }
#btn-stash { background: #3b3a32; color: #e0af68; }
#btn-merge { background: #41242c; color: #f7768e; }
#btn-remote { background: #2b3c54; color: #2ac3de; }

Button:hover {
    background: #565f89;
}

#log-container {
    height: 1fr;
    background: #101014;
    border: tall #3b4261;
    border-title-color: #7aa2f7;
    padding: 1;
}

RichLog {
    background: #101014;
    color: #a9b1d6;
}

.alert-card {
    background: #2a1f21;
    border: solid #f7768e;
    color: #f7768e;
    padding: 1;
    margin-bottom: 1;
    text-align: center;
    text-style: bold;
    height: 5;
}

.warning-card {
    background: #2a241f;
    border: solid #e0af68;
    color: #e0af68;
    padding: 1;
    margin-bottom: 1;
    text-align: center;
    text-style: bold;
    height: 5;
}

.info-card {
    background: #1f2335;
    border: solid #7aa2f7;
    color: #7aa2f7;
    padding: 1;
    margin-bottom: 1;
    text-align: center;
    text-style: bold;
    height: 5;
}

.status-label {
    margin-bottom: 1;
    color: #a9b1d6;
}

/* Modals general styling */
#modal-container, #modal-container-large {
    background: #1f2335;
    border: thick #7aa2f7;
    padding: 2;
    width: 60;
    height: 25;
    align: center middle;
}

#modal-container-large {
    width: 70;
    height: 25;
}

#modal-title {
    text-style: bold;
    color: #ff9e64;
    margin-bottom: 1;
    text-align: center;
}

#modal-message {
    margin-bottom: 2;
    text-align: center;
}

#modal-buttons, #modal-buttons-three {
    margin-top: 2;
    align: center middle;
    height: 3;
}

#modal-buttons Button {
    width: 20;
    margin: 0 1;
}

#modal-buttons-three Button {
    width: 18;
    margin: 0 1;
}

Select {
    margin-bottom: 1;
    width: 100%;
}

Input {
    margin-bottom: 1;
    width: 100%;
}

#type-description {
    color: #9abdf5;
    margin-bottom: 1;
    text-style: italic;
    height: 2;
}
"""


class CompusApp(App):
    TITLE = "Compus - Git Repository Manager"
    BINDINGS = [
        Binding("c", "commit", "Commit", show=True),
        Binding("p", "pull", "Pull", show=True),
        Binding("u", "push", "Push", show=True),
        Binding("b", "branch", "Branches", show=True),
        Binding("s", "stash", "Stash", show=True),
        Binding("m", "merge", "Merge", show=True),
        Binding("g", "remote", "Set Remote", show=True),
        Binding("r", "refresh", "Refresh Status", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    CSS = CSS

    def __init__(self, repo_path=None):
        super().__init__()
        self.git = GitHelper(repo_path)
        self.path = repo_path or os.getcwd()

    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container(id="layout"):
            # Left Sidebar: Git Status and Alerts
            with Vertical(id="left-sidebar"):
                self.title_label = Label("📊 REPO SUMMARY", id="sidebar-title")
                self.branch_label = Label("🌿 Active Branch: Loading...")
                self.staged_label = Label("Staged files: 0")
                self.modified_label = Label("Modified (unstaged) files: 0")
                self.untracked_label = Label("Untracked files: 0")
                
                # Reactive Alert containers
                self.commit_alert = Static("", classes="warning-card")
                self.pull_alert = Static("", classes="alert-card")
                
                yield self.title_label
                yield self.branch_label
                yield self.staged_label
                yield self.modified_label
                yield self.untracked_label
                
                yield self.commit_alert
                yield self.pull_alert
                
            # Right Panel: Quick Commands & Console Output
            with Vertical(id="main-panel"):
                # Action Buttons Grid (4 columns)
                with Container(id="action-buttons"):
                    yield Button("💬 [C] Commit", id="btn-commit")
                    yield Button("⬇️ [P] Pull", id="btn-pull")
                    yield Button("⬆️ [U] Push", id="btn-push")
                    yield Button("🌿 [B] Branches", id="btn-branch")
                    yield Button("📦 [S] Stash", id="btn-stash")
                    yield Button("🔀 [M] Merge", id="btn-merge")
                    yield Button("🌐 [G] Remote", id="btn-remote")
                
                # Logs container
                with Container(id="log-container"):
                    self.log_widget = RichLog(highlight=True, markup=True)
                    yield self.log_widget
                    
        yield Footer()

    def on_mount(self) -> None:
        # Set titles
        self.title_label.update(f"📊 REPO: {os.path.basename(self.path).upper()}")
        self.query_one("#left-sidebar").border_title = "Git Repository Summary"
        self.query_one("#log-container").border_title = "Command Console Logs"
        
        # Check if is actual git repo
        if not self.git.is_git_repo():
            self.log_widget.write("[bold red]❌ ERROR: The current directory is not a git repository.[/bold red]")
            self.log_widget.write("[yellow]Please run 'git init' or open Compus inside a valid Git repository folder.[/yellow]")
            self.branch_label.update("🌿 Active Branch: [bold red]NOT A GIT REPO[/bold red]")
            # Disable actions
            for btn in self.query("Button"):
                btn.disabled = True
            return

        self.log_widget.write(f"[bold green]🚀 Welcome to Compus![/bold green] Managing repo at: [bold cyan]{self.path}[/bold cyan]\n")
        self.refresh_status()

    def refresh_status(self) -> None:
        """Retrieves latest branch, files status, and sync state to update the UI."""
        if not self.git.is_git_repo():
            return

        branch = self.git.get_current_branch()
        self.branch_label.update(f"🌿 Active Branch: [bold cyan]{branch}[/bold cyan]")
        
        status = self.git.get_status_summary()
        self.staged_label.update(f"   [green]●[/green] Staged files: [bold]{len(status['staged'])}[/bold]")
        self.modified_label.update(f"   [yellow]●[/yellow] Modified (unstaged): [bold]{len(status['modified'])}[/bold]")
        self.untracked_label.update(f"   [red]●[/red] Untracked files: [bold]{len(status['untracked'])}[/bold]")

        # 1. LOCAL CHANGES ALERT
        total_uncommitted = len(status["modified"]) + len(status["untracked"]) + len(status["staged"])
        if total_uncommitted > 8:
            self.commit_alert.update(f"⚠️ HIGH LOCAL CHANGES ({total_uncommitted})\nConsider making a commit to save progress!")
            self.commit_alert.display = True
        elif total_uncommitted > 0:
            self.commit_alert.update(f"⚠️ {total_uncommitted} changes waiting for commit.")
            self.commit_alert.display = True
        else:
            self.commit_alert.display = False

        # 2. REMOTE SYNC ALERTS
        remote_url = self.git.get_remote_url()
        if not remote_url:
            self.pull_alert.update("💡 Remote URL not configured!\nPress [G] to connect to GitHub.")
            self.pull_alert.classes = "info-card"
            self.pull_alert.display = True
            return

        ahead, behind, err = self.git.get_sync_status()
        if err:
            if "upstream" in err.lower():
                self.pull_alert.update("💡 Upstream not set for this branch.\nPush to create remote branch.")
                self.pull_alert.classes = "info-card"
                self.pull_alert.display = True
            else:
                self.pull_alert.display = False
        else:
            if behind > 0:
                self.pull_alert.update(f"⚠️ BEHIND BY {behind} COMMITS!\nRun Git Pull to download remote changes safely.")
                self.pull_alert.classes = "alert-card"
                self.pull_alert.display = True
            elif ahead > 0:
                self.pull_alert.update(f"ℹ️ Ahead by {ahead} commits.\nReady to push changes.")
                self.pull_alert.classes = "info-card"
                self.pull_alert.display = True
            else:
                self.pull_alert.display = False

    # Action Handlers / Bindings
    def action_refresh(self) -> None:
        self.log_widget.write("[blue]🔄 Refreshing repository status...[/blue]")
        # Silent fetch in background to verify behind/ahead status
        self.git.fetch()
        self.refresh_status()
        self.log_widget.write("[green]✓ Status refreshed successfully.[/green]")

    def action_commit(self) -> None:
        self.press_button("btn-commit")

    def action_pull(self) -> None:
        self.press_button("btn-pull")

    def action_push(self) -> None:
        self.press_button("btn-push")

    def action_branch(self) -> None:
        self.press_button("btn-branch")

    def action_stash(self) -> None:
        self.press_button("btn-stash")

    def action_merge(self) -> None:
        self.press_button("btn-merge")

    def action_remote(self) -> None:
        self.press_button("btn-remote")

    def press_button(self, button_id: str) -> None:
        try:
            self.query_one(f"#{button_id}").press()
        except Exception:
            pass

    # Button click actions
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-commit":
            self.push_screen(CommitModal(), self.handle_commit_result)
            
        elif event.button.id == "btn-pull":
            self.push_screen(
                ConfirmModal(
                    message="Do you want to run 'git pull' to fetch and integrate remote changes?",
                    title="Confirm Git Pull"
                ),
                self.handle_pull_result
            )
            
        elif event.button.id == "btn-push":
            self.push_screen(
                ConfirmModal(
                    message="Do you want to run 'git push' to upload your local commits to the remote branch?",
                    title="Confirm Git Push"
                ),
                self.handle_push_result
            )
            
        elif event.button.id == "btn-branch":
            current = self.git.get_current_branch()
            branches = self.git.get_branches()
            self.push_screen(BranchModal(current, branches), self.handle_branch_result)
            
        elif event.button.id == "btn-stash":
            self.push_screen(StashModal(), self.handle_stash_result)
            
        elif event.button.id == "btn-merge":
            current = self.git.get_current_branch()
            branches = self.git.get_branches()
            if len(branches) <= 1:
                self.log_widget.write("[yellow]⚠️ Cannot merge: No other local branches exist.[/yellow]")
                return
            self.push_screen(MergeModal(current, branches), self.handle_merge_result)
            
        elif event.button.id == "btn-remote":
            current_url = self.git.get_remote_url()
            self.push_screen(RemoteModal(current_url), self.handle_remote_result)

    # Callbacks for modal results
    def handle_commit_result(self, result: tuple[str, str] | None) -> None:
        if not result:
            self.log_widget.write("[yellow]Commit cancelled by user.[/yellow]")
            return
            
        commit_type, message = result
        self.log_widget.write(f"[yellow]Executing commit with type: '{commit_type}'...[/yellow]")
        success, output = self.git.commit(commit_type, message)
        
        if success:
            self.log_widget.write(f"[bold green]✓ Commit Applied successfully![/bold green]")
            self.log_widget.write(f"[dim]{output}[/dim]\n")
        else:
            self.log_widget.write(f"[bold red]❌ Commit Failed:[/bold red]\n[red]{output}[/red]\n")
            
        self.refresh_status()

    def handle_pull_result(self, confirmed: bool) -> None:
        if not confirmed:
            self.log_widget.write("[yellow]Pull cancelled by user.[/yellow]")
            return
            
        self.log_widget.write("[yellow]Executing git pull...[/yellow]")
        success, output = self.git.pull()
        
        if success:
            self.log_widget.write("[bold green]✓ Git Pull Applied successfully![/bold green]")
            self.log_widget.write(f"[dim]{output}[/dim]\n")
        else:
            self.log_widget.write(f"[bold red]❌ Git Pull Failed:[/bold red]\n[red]{output}[/red]\n")
            
        self.refresh_status()

    def handle_push_result(self, confirmed: bool) -> None:
        if not confirmed:
            self.log_widget.write("[yellow]Push cancelled by user.[/yellow]")
            return
            
        self.log_widget.write("[yellow]Executing git push...[/yellow]")
        success, output = self.git.push()
        
        if success:
            self.log_widget.write("[bold green]✓ Git Push Applied successfully![/bold green]")
            self.log_widget.write(f"[dim]{output}[/dim]\n")
        else:
            self.log_widget.write(f"[bold red]❌ Git Push Failed:[/bold red]\n[red]{output}[/red]\n")
            
        self.refresh_status()

    def handle_branch_result(self, result: tuple[str, str, str] | None) -> None:
        if not result:
            self.log_widget.write("[yellow]Branch action cancelled.[/yellow]")
            return
            
        action, branch_name, _ = result
        if action == "checkout":
            self.log_widget.write(f"[yellow]Switching to branch '{branch_name}'...[/yellow]")
            success, output = self.git.checkout_branch(branch_name)
        elif action == "create":
            self.log_widget.write(f"[yellow]Creating and switching to new branch '{branch_name}'...[/yellow]")
            success, output = self.git.create_and_checkout_branch(branch_name)
            
        if success:
            self.log_widget.write(f"[bold green]✓ Switch branch success![/bold green] Now on: [bold cyan]{branch_name}[/bold cyan]")
            self.log_widget.write(f"[dim]{output}[/dim]\n")
        else:
            self.log_widget.write(f"[bold red]❌ Branch switch failed:[/bold red]\n[red]{output}[/red]\n")
            
        self.refresh_status()

    def handle_stash_result(self, stash_msg: str | None) -> None:
        if stash_msg is None:
            # Let's check if they want to POP the stash instead, or if they cancelled
            self.push_screen(
                ConfirmModal(
                    message="Would you like to POP (restore) the most recent stash onto your working tree?",
                    title="Restore Stash (Pop)"
                ),
                self.handle_stash_pop_confirm
            )
            return

        self.log_widget.write("[yellow]Stashing current local changes...[/yellow]")
        success, output = self.git.stash_push(stash_msg)
        
        if success:
            self.log_widget.write("[bold green]✓ Changes stashed successfully![/bold green]")
            self.log_widget.write(f"[dim]{output}[/dim]\n")
        else:
            self.log_widget.write(f"[bold red]❌ Git Stash Failed:[/bold red]\n[red]{output}[/red]\n")
            
        self.refresh_status()

    def handle_stash_pop_confirm(self, confirmed: bool) -> None:
        if not confirmed:
            self.log_widget.write("[yellow]Stash action cancelled.[/yellow]")
            return
            
        self.log_widget.write("[yellow]Popping latest stash...[/yellow]")
        success, output = self.git.stash_pop()
        
        if success:
            self.log_widget.write("[bold green]✓ Stash popped successfully![/bold green]")
            self.log_widget.write(f"[dim]{output}[/dim]\n")
        else:
            self.log_widget.write(f"[bold red]❌ Git Stash Pop Failed (maybe no stashes exist or conflicts occurred):[/bold red]\n[red]{output}[/red]\n")
            
        self.refresh_status()

    def handle_merge_result(self, branch_to_merge: str | None) -> None:
        if not branch_to_merge:
            self.log_widget.write("[yellow]Merge action cancelled.[/yellow]")
            return
            
        self.log_widget.write(f"[yellow]Merging branch '{branch_to_merge}' into current branch...[/yellow]")
        success, output = self.git.merge(branch_to_merge)
        
        if success:
            self.log_widget.write(f"[bold green]✓ Merge applied successfully![/bold green]")
            self.log_widget.write(f"[dim]{output}[/dim]\n")
        else:
            self.log_widget.write(f"[bold red]❌ Merge Failed or requires manual conflict resolution:[/bold red]\n[red]{output}[/red]\n")
            
        self.refresh_status()

    def handle_remote_result(self, url: str | None) -> None:
        if url is None:
            self.log_widget.write("[yellow]Remote configuration cancelled.[/yellow]")
            return
            
        if not url:
            self.log_widget.write("[yellow]No Remote URL was specified.[/yellow]")
            return
            
        self.log_widget.write(f"[yellow]Configuring remote 'origin' with URL: '{url}'...[/yellow]")
        success, output = self.git.set_remote_url(url)
        
        if success:
            self.log_widget.write(f"[bold green]✓ Remote 'origin' configured successfully to {url}![/bold green]")
            self.log_widget.write(f"[dim]{output}[/dim]\n")
        else:
            self.log_widget.write(f"[bold red]❌ Failed to set remote:[/bold red]\n[red]{output}[/red]\n")
            
        self.refresh_status()


def run_app():
    # If a path was passed in sys.argv, use it. Otherwise use current working dir.
    repo_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    app = CompusApp(repo_path)
    app.run()


if __name__ == "__main__":
    run_app()
