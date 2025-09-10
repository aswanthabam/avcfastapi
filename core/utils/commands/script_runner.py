# core/scripts.py
import importlib.util
from pathlib import Path
import sys
import argparse
import asyncio
from inspect import iscoroutinefunction

COMMANDS_FOLDER = "apps/management/commands"  # hardcoded folder


class ScriptRunner:
    def __init__(self, commands_folder=COMMANDS_FOLDER):
        self.commands_folder = Path(commands_folder)
        self.commands = self.load_commands()

    def load_commands(self):
        if not self.commands_folder.exists():
            print(f"Folder {self.commands_folder} does not exist.")
            return {}

        sys.path.insert(0, str(self.commands_folder.parent))
        commands = {}

        for file in self.commands_folder.glob("*.py"):
            if file.name.startswith("__"):
                continue
            module_name = file.stem  # filename without extension
            spec = importlib.util.spec_from_file_location(module_name, str(file))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find subclass of Command
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                try:
                    from .command import Command as BaseCommand

                    if issubclass(attr, BaseCommand) and attr != BaseCommand:
                        commands[module_name] = attr  # use filename as key
                except TypeError:
                    continue
        return commands

    def get_command(self, name):
        return self.commands.get(name)

    def run(self, command_name, argv=None):
        command_class = self.get_command(command_name)
        if not command_class:
            print(f"Command '{command_name}' not found.")
            return

        command_instance = command_class()
        cmd_parser = argparse.ArgumentParser(prog=command_name)
        command_instance.add_arguments(cmd_parser)
        args = cmd_parser.parse_args(argv)
        options = vars(args)

        # Check if handle is async
        if iscoroutinefunction(command_instance.handle):
            asyncio.run(command_instance.handle(**options))
        else:
            command_instance.handle(**options)
