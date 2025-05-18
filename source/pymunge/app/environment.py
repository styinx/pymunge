from logging import Logger

from app.diagnostic import Diagnostic
from app.registry import FileRegistry
from util.logging import get_logger


logger = get_logger(__name__)


class MungeEnvironment:
    def __init__(self, logger: Logger = logger):
        self.diagnostic: Diagnostic = Diagnostic(logger=logger)
        self.registry: FileRegistry = FileRegistry()