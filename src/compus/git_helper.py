import subprocess
import os

class GitHelper:
    def __init__(self, repo_path=None):
        self.repo_path = repo_path or os.getcwd()

    def _run(self, args: list[str]) -> tuple[int, str, str]:
        """Runs a git command in the target repository path and returns (returncode, stdout, stderr)"""
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=True  # Helpful for Windows resolving git properly
            )
            return res.returncode, res.stdout.strip(), res.stderr.strip()
        except Exception as e:
            return -1, "", str(e)

    def is_git_repo(self) -> bool:
        code, stdout, _ = self._run(["rev-parse", "--is-inside-work-tree"])
        return code == 0 and stdout == "true"

    def get_current_branch(self) -> str:
        code, stdout, _ = self._run(["branch", "--show-current"])
        if code == 0 and stdout:
            return stdout
        # Fallback for detached HEAD
        code, stdout, _ = self._run(["rev-parse", "--abbrev-ref", "HEAD"])
        return stdout if code == 0 else "N/A"

    def get_status_summary(self) -> dict:
        """Returns lists of modified, untracked, and staged files."""
        # Get porcelain status for easy parsing
        code, stdout, _ = self._run(["status", "--porcelain"])
        summary = {
            "staged": [],
            "modified": [],
            "untracked": [],
            "total_changes": 0
        }
        if code != 0 or not stdout:
            return summary

        for line in stdout.splitlines():
            if len(line) < 4:
                continue
            x = line[0]  # Stage status
            y = line[1]  # Working tree status
            file_path = line[3:]

            if x in ("M", "A", "D", "R", "C"):
                summary["staged"].append(file_path)
            
            if y == "M" or y == "D":
                summary["modified"].append(file_path)
            elif x == "?" and y == "?":
                summary["untracked"].append(file_path)

        summary["total_changes"] = len(summary["staged"]) + len(summary["modified"]) + len(summary["untracked"])
        return summary

    def get_sync_status(self) -> tuple[int, int, str]:
        """Returns (ahead_count, behind_count, error_msg).
        Ahead: local commits not pushed. Behind: remote commits not pulled.
        """
        # First check if there is an upstream branch
        branch = self.get_current_branch()
        if not branch or branch == "HEAD" or branch == "N/A":
            return 0, 0, "No active branch"

        code, _, _ = self._run(["rev-parse", "--abbrev-ref", f"{branch}@{'{u}'}"])
        if code != 0:
            return 0, 0, "No remote upstream tracking branch set."

        # Count ahead
        code_a, stdout_a, err_a = self._run(["rev-list", "--count", f"@{'{u}'}..HEAD"])
        # Count behind
        code_b, stdout_b, err_b = self._run(["rev-list", "--count", f"HEAD..@{'{u}'}"])

        ahead = int(stdout_a) if (code_a == 0 and stdout_a.isdigit()) else 0
        behind = int(stdout_b) if (code_b == 0 and stdout_b.isdigit()) else 0

        return ahead, behind, ""

    def get_remote_url(self) -> str:
        """Queries the URL for the 'origin' remote repository."""
        code, stdout, _ = self._run(["remote", "get-url", "origin"])
        return stdout if code == 0 else ""

    def set_remote_url(self, url: str) -> tuple[bool, str]:
        """Sets or adds the 'origin' remote repository URL."""
        current_remote = self.get_remote_url()
        if current_remote:
            code, stdout, stderr = self._run(["remote", "set-url", "origin", url])
        else:
            code, stdout, stderr = self._run(["remote", "add", "origin", url])
        return code == 0, stdout or stderr

    def fetch(self) -> tuple[bool, str]:
        code, stdout, stderr = self._run(["fetch"])
        return code == 0, stdout or stderr

    def commit(self, commit_type: str, message: str) -> tuple[bool, str]:
        # Automatically stage all changes (including new/untracked ones) if nothing is staged
        status = self.get_status_summary()
        if not status["staged"] and (status["modified"] or status["untracked"]):
            self._run(["add", "."])

        code, stdout, stderr = self._run(["commit", "-m", f"{commit_type}: {message}"])
        return code == 0, stdout if code == 0 else stderr

    def pull(self) -> tuple[bool, str]:
        code, stdout, stderr = self._run(["pull", "--no-rebase"])
        return code == 0, stdout or stderr

    def push(self) -> tuple[bool, str]:
        branch = self.get_current_branch()
        code, stdout, stderr = self._run(["push", "origin", branch])
        # If upstream is not set, push and set upstream
        if "has no upstream branch" in stderr or "no upstream branch" in stderr.lower():
            code, stdout, stderr = self._run(["push", "--set-upstream", "origin", branch])
        return code == 0, stdout or stderr

    def get_branches(self) -> list[str]:
        code, stdout, _ = self._run(["branch", "--format=%(refname:short)"])
        if code == 0 and stdout:
            return [line.strip() for line in stdout.splitlines() if line.strip()]
        return []

    def checkout_branch(self, branch: str) -> tuple[bool, str]:
        code, stdout, stderr = self._run(["checkout", branch])
        return code == 0, stdout or stderr

    def create_and_checkout_branch(self, branch: str) -> tuple[bool, str]:
        code, stdout, stderr = self._run(["checkout", "-b", branch])
        return code == 0, stdout or stderr

    def stash_push(self, message: str = "") -> tuple[bool, str]:
        args = ["stash", "push"]
        if message:
            args += ["-m", message]
        code, stdout, stderr = self._run(args)
        return code == 0, stdout or stderr

    def stash_pop(self) -> tuple[bool, str]:
        code, stdout, stderr = self._run(["stash", "pop"])
        return code == 0, stdout or stderr

    def merge(self, branch: str) -> tuple[bool, str]:
        code, stdout, stderr = self._run(["merge", branch, "--no-edit"])
        return code == 0, stdout or stderr
