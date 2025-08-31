import pickle

from app.registry import FileRegistry
from util.diagnostic import Diagnostic
from util.logging import get_logger, ScopedLogger
from util.statistic import Statistic


class MungeEnvironment:
    """
    Singleton class which is initialized once in the :class:`Munger`.
    Provides access to the :class:`Diagnostic`, :class:`ScopedLogger`,
    :class:`Registry`, and :class:`Statistic`.
    """

    Diag: Diagnostic = None
    Log: ScopedLogger = None
    Reg: FileRegistry = None
    Stat: Statistic = None

    def __init__(self, args, logger: ScopedLogger = get_logger(__name__)):
        self.logger: ScopedLogger = logger
        self.diagnostic: Diagnostic = Diagnostic(logger=logger)
        self.registry: FileRegistry = FileRegistry(args, diagnostic=self.diagnostic, logger=logger)
        self.statistic: Statistic = Statistic()

        if not MungeEnvironment.Diag:
            MungeEnvironment.Diag = self.diagnostic
        if not MungeEnvironment.Log:
            MungeEnvironment.Log = self.logger
        if not MungeEnvironment.Reg:
            MungeEnvironment.Reg = self.registry
        if not MungeEnvironment.Stat:
            MungeEnvironment.Stat = self.statistic

        if args.munge.cache:
            self.cache_file = args.cache.file

    def store_cache(self):
        pickle.dump({
            'diagnostic': self.diagnostic,
            'statistic': self.statistic,
        }, self.cache_file.open('wb+'))

        self.logger.info(f'Storing cache to file "{self.cache_file}"')

    def load_cache(self):
        self.logger.info(f'Loading cache from file "{self.cache_file}"')

        dump = pickle.load(self.cache_file.open('rb'))

        self.diagnostic = dump['diagnostic']
        self.statistic = dump['statistic']

    def details(self):
        self.statistic.details()
        self.diagnostic.details()

    def summary(self):
        self.statistic.summary()
        self.diagnostic.summary()
