from app.diagnostic import Diagnostic
from app.registry import FileRegistry
from app.statistic import Statistic
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
        self.diagnostic: Diagnostic = Diagnostic(logger=logger)
        self.registry: FileRegistry = FileRegistry()
        self.statistic: Statistic = Statistic()

        if not MungeEnvironment.Diagnostic:
            MungeEnvironment.Diagnostic = self.diagnostic
        if not MungeEnvironment.Registry:
            MungeEnvironment.Registry = self.registry
        if not MungeEnvironment.Statistic:
            MungeEnvironment.Statistic = self.statistic
