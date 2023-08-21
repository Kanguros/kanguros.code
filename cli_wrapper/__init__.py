import subprocess
from subprocess import run, CompletedProcess
from typing import List, Optional, Dict


class PACLI:
    def __init__(self, username: str, password: str, vault_url: str, exe_dir: str = ".",
                 defaults: Optional[Dict[str, str]] = None):
        """
        Initialize the PACLI wrapper.

        Args:
            username (str): Username for logging in.
            password (str): Password for logging in.
            vault_url (str): URL of the Vault.
            exe_dir (str, optional): Directory containing PACLI executable. Defaults to ".".
            defaults (dict, optional): Dictionary of default PACLI values. Defaults to None.
        """
        self.username = username
        self.password = password
        self.vault_url = vault_url
        self.exe_dir = exe_dir

        self.defaults = {
            "VAULT": "PWV",
            "FOLDER": "Root",
            "USER": self.username
        }
        if defaults:
            self.defaults.update(defaults)

        self._start = self._define_start()

        self._end = [
            ["PACLI", "LOGOFF"],
            ["PACLI", "TERM"],
        ]

    def _define_start(self) -> List[List[str]]:
        """
        Define the PACLI start commands with default values.

        Returns:
            List[List[str]]: List of start command lists.
        """
        defaults = [f"{k.upper()}={v}" for k, v in self.defaults.items()]
        return [
            ["PACLI", "INIT"],
            ["PACLI", "DEFAULT", *defaults],
            ["PACLI", "DEFINE", f"ADDRESS={self.vault_url}"],
        ]

    def run(self, cmd: List[str], **kwargs) -> CompletedProcess:
        """
        Execute a command using subprocess.

        Args:
            cmd (List[str]): List of command arguments.
            **kwargs: Additional keyword arguments for subprocess.run.

        Returns:
            CompletedProcess: CompletedProcess object.
        """
        return run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.exe_dir, **kwargs)

    def run_many(self, cmds: List[List[str]], **kwargs) -> List[CompletedProcess]:
        """
        Execute multiple commands using subprocess.

        Args:
            cmds (List[List[str]]): List of lists containing command arguments.
            **kwargs: Additional keyword arguments for subprocess.run.

        Returns:
            List[CompletedProcess]: List of CompletedProcess objects.
        """
        return [self.run(cmd, **kwargs) for cmd in cmds]

    def logon(self):
        """
        Log on to the Vault.
        """
        self.run_many(self._start, check=True)

    def logoff(self):
        """
        Log off from the Vault.
        """
        self.run_many(self._end)

    def __enter__(self):
        self.logon()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logoff()

    def cmd_open_safe(self, safe_name: str) -> List[List[str]]:
        """
        Open a safe with the specified name.

        Args:
            safe_name (str): Name of the safe to open.

        Returns:
            List[List[str]]: List of commands to open the safe.
        """
        return [
            ["PACLI", "OPENSAFE", f"SAFE={safe_name}"]
        ]

    def cmd_close_safe(self, safe_name: str) -> List[List[str]]:
        """
        Close a safe with the specified name.

        Args:
            safe_name (str): Name of the safe to close.

        Returns:
            List[List[str]]: List of commands to close the safe.
        """
        return [
            ["PACLI", "CLOSESAFE", f"SAFE={safe_name}"]
        ]

    def cmd_unlock_accounts(self, safe_name: str, accounts: List[str]) -> List[List[str]]:
        """
        Unlock an accounts with the specified names. Include openning and closing a safe.

        Args:
            safe_name (str): Name of the safe with accounts.
            accounts (List[str]): List of accounts name.

        Returns:
            List[List[str]]: List of commands to unlock the accounts.
        """
        unlock_cmd = [
            ["UNLOCKFILE", f"SAFE={safe_name}", f"FILE={account}"]
            for account in accounts
        ]
        return [*self.cmd_open_safe(safe_name),
                *unlock_cmd,
                self.cmd_close_safe(safe_name)]

    def unlock_account(self, safe_name: str, account: str):
        accounts = [account]
        return self.run_many(self.cmd_unlock_accounts(safe_name, accounts))

    def unlock_accounts(self, safe_name: str, accounts: List[str]):
        return self.run_many(self.cmd_unlock_accounts(safe_name, accounts))


def get_pacli() -> PACLI:
    """
    Get an instance of the PACLI wrapper.

    Returns:
        PACLI: Instance of PACLI class.
    """
    username = "USERNAME"
    password = "PASSWORD"
    vault = "http://localhost"
    return PACLI(username, password, vault)
