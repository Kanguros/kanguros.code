import importlib
import logging
import os
from typing import Optional, Callable, List

import click

logger = logging.getLogger(__name__)


class LazyLoadGroup(click.Group):
    """A custom Click Group that lazily loads subcommands from specified packages."""

    def __init__(self, commands_dir: str = "tasks", *args, **kwargs):
        """
        Initialize the LazyLoadGroup.

        Args:
            commands_dir (str): Name of the inner package directory with groups..
        """
        super(LazyLoadGroup, self).__init__(*args, **kwargs)
        self._subcommands_loaded = False
        self.commands_dir = commands_dir

        self._curr_dirname = os.path.dirname(__file__)
        self.source_dir = os.path.join(self._curr_dirname, self.commands_dir)
        self.source_package = os.path.basename(self._curr_dirname) + "." + self.commands_dir

        logger.debug(
            f"LazyLoadGroup initialized with source_dir: {self.source_dir}, source_package: {self.source_package}")

    def list_commands(self, ctx: click.Context) -> List[str]:
        """
        List available subcommands.

        Args:
            ctx (click.Context): Click context.

        Returns:
            List[str]: List of available subcommands.
        """
        if not self._subcommands_loaded:
            self.load_subcommands(ctx)
        return super(LazyLoadGroup, self).list_commands(ctx)

    def load_subcommands(self, ctx: click.Context) -> None:
        """
        Load subcommands dynamically from specified packages.

        Args:
            ctx (click.Context): Click context.
        """
        src_dir = self.source_dir
        logger.debug(f"Loading subcommands from {src_dir}")

        for path in os.listdir(src_dir):
            if path == 'tasks':
                continue
            if path.startswith("_") or path.startswith("."):
                continue
            if not os.path.isdir(os.path.join(src_dir, path)):
                continue
            self.load_group(path)

    def load_group(self, group_name: str):
        logger.debug(f"[Group:{group_name}] Loading new group")
        group = click.Group(name=group_name)
        group_dir = os.path.join(self.source_dir, group_name)

        logger.debug(f"[Group:{group_name}] Looking for commands in path: {group_dir}")
        for filename in os.listdir(group_dir):
            if not filename.endswith('.py'):
                continue
            if filename.startswith("__"):
                continue
            command_name = os.path.splitext(filename)[0]
            logger.debug(f"[Group:{group_name}] Importing a module [{filename}]. Looking for function [{command_name}]")

            command = self.import_command(group_name, command_name)
            group.add_command(command, name=command_name)

            logger.debug(f"[Group:{group_name}] Added command: {command_name}")

        self.add_command(group, name=group_name)

    def import_command(self, module_name: str, command_name: str):
        """
        Import a module dynamically.

        Args:
            module_name (str): Path to the module.
            command_name (str): Name of the command.

        Returns:
            Callable: Imported module.
        """
        module_path = f'{self.source_package}.{module_name}.{command_name}'
        logger.debug(f"Importing module: {module_path}")
        module = importlib.import_module(module_path)
        logger.debug(f"Getting a function: {command_name}")
        function = getattr(module, command_name)
        return function

    def get_command(self, ctx: click.Context, cmd_name: str) -> Callable:
        """
        Get the command function based on the command name.

        Args:
            ctx (click.Context): Click context.
            cmd_name (str): Name of the command.

        Returns:
            Callable: The command function.

        Raises:
            click.ClickException: Raised if the command is not found.
        """
        if cmd_name not in self.commands:
            self.load_group(cmd_name)
        return self.commands[cmd_name]


@click.group(cls=LazyLoadGroup, no_args_is_help=True)
def cli() -> None:
    """
    Main command entry point.
    """
