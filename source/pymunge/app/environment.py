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
        self.statistic: Statistic = Statistic()

        if not MungeEnvironment.Diag and self.diagnostic:
            MungeEnvironment.Diag = self.diagnostic
        if not MungeEnvironment.Log and self.logger:
            MungeEnvironment.Log = self.logger
        if not MungeEnvironment.Stat and self.statistic:
            MungeEnvironment.Stat = self.statistic

        if args.run == 'cache':
            self.import_cache_file = args.cache.file

        elif args.run == 'format':
            self.registry: FileRegistry = FileRegistry(
                source=args.format.directory,
                target=args.munge.target,
                diagnostic=self.diagnostic,
                logger=logger
            )
            MungeEnvironment.Reg = self.registry

        elif args.run == 'munge':
            self.registry: FileRegistry = FileRegistry(
                source=args.munge.source,
                target=args.munge.target,
                diagnostic=self.diagnostic,
                logger=logger
            )

            if not MungeEnvironment.Reg and self.registry:
                MungeEnvironment.Reg = self.registry

            self.export_cache_file = args.munge.cache_file

    def store_cache(self):
        pickle.dump({
            'diagnostic': self.diagnostic,
            'statistic': self.statistic,
        }, self.export_cache_file.open('wb+'))

        self.logger.info(f'Store cache file: "{self.export_cache_file}"')

    def load_cache(self):
        self.logger.info(f'Load cache file: "{self.import_cache_file}"')

        dump = pickle.load(self.import_cache_file.open('rb'))

        self.diagnostic = dump['diagnostic']
        self.statistic = dump['statistic']

    def details(self):
        self.statistic.details()
        self.diagnostic.details()

    def summary(self):
        self.statistic.summary()
        self.diagnostic.summary()
