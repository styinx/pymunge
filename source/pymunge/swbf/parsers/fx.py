from logging import Logger
from pathlib import Path

from parxel.nodes import Node, LexicalNode
from parxel.token import TK, Token

from app.environment import MungeEnvironment as ENV
from swbf.parsers.parser import SwbfTextParser
from swbf.parsers.cfg import CfgParser
from util.diagnostic import WarningMessage
from util.enum import Enum
from util.logging import get_logger


class FxWarning(WarningMessage):
    scope = 'FX'

class FxParser(CfgParser):
    extension = 'fx'

    def __init__(self, filepath: Path, tokens: list[Token] = None, logger: Logger = get_logger(__name__)):
        SwbfTextParser.__init__(self, filepath=filepath, tokens=tokens, logger=logger)


if __name__ == '__main__':
    FxParser.cmd_helper()
