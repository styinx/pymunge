from logging import Logger

from app.diagnostic import Diagnostic
from app.registry import FileRegistry
from app.statistic import Statistic
from util.logging import get_logger


class MungeEnvironment:
    Diagnostic = None
    Registry = None
    Statistic = None

    def __init__(self, logger: Logger = get_logger(__name__)):
        self.diagnostic: Diagnostic = Diagnostic(logger=logger)
        self.registry: FileRegistry = FileRegistry()
        self.statistic: Statistic = Statistic()

        if not MungeEnvironment.Diagnostic:
            MungeEnvironment.Diagnostic = self.diagnostic
        if not MungeEnvironment.Registry:
            MungeEnvironment.Registry = self.registry
        if not MungeEnvironment.Statistic:
            MungeEnvironment.Statistic = self.statistic