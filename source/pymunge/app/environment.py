from pathlib import Path
import pickle

from app.registry import FileRegistry
from app.statistic import Statistic
from util.diagnostic import Diagnostic
from util.logging import get_logger, ScopedLogger


class MungeEnvironment:
    """
    Singleton class which is initialized once in the :class:`Munger`.
    Provides access to the :class:`Diagnostic`, :class:`Registry`, and
    :class:`Statistic`.
    """

    Diagnostic = None
    Registry = None
    Statistic = None

    def __init__(self, logger: ScopedLogger = get_logger(__name__)):
        self.logger: ScopedLogger = logger
        self.diagnostic: Diagnostic = Diagnostic(logger=logger)
        self.registry: FileRegistry = FileRegistry()
        self.statistic: Statistic = Statistic()

        if not MungeEnvironment.Diagnostic:
            MungeEnvironment.Diagnostic = self.diagnostic
        if not MungeEnvironment.Registry:
            MungeEnvironment.Registry = self.registry
        if not MungeEnvironment.Statistic:
            MungeEnvironment.Statistic = self.statistic

    def store(self, file: Path):
        pickle.dump({
            'diagnostic': self.diagnostic,
            'statistic': self.statistic,
        }, file.open('wb+'))

        self.logger.info(f'Storing cache to file "{file}"')

    def load(self, file: Path):
        self.logger.info(f'Loading cache from file "{file}"')

        dump = pickle.load(file.open('rb'))

        self.diagnostic = dump['diagnostic']
        self.statistic = dump['statistic']

    def details(self):
        self.statistic.details()
        self.diagnostic.details()

    def summary(self):
        self.statistic.summary()
        self.diagnostic.summary()
