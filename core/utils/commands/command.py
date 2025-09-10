# apps/management/commands.py
from abc import ABC, abstractmethod
import argparse


class Command(ABC):
    help = ""  # Optional description

    def __init__(self):
        pass

    def add_arguments(self, parser: argparse.ArgumentParser):
        """
        Override this to define command-specific arguments
        Example:
            parser.add_argument("--limit", type=int, default=10)
        """
        pass

    @abstractmethod
    def handle(self, *args, **options):
        """
        Logic of the command goes here
        """
        raise NotImplementedError("Subclasses must implement this method")
