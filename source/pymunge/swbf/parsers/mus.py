from logging import Logger
from pathlib import Path

from parxel.token import Token

from swbf.parsers.parser import SwbfTextParser
from swbf.parsers.cfg import CfgParser
from util.diagnostic import WarningMessage
from util.logging import get_logger


class MusWarning(WarningMessage):
    TOPIC = 'MUS'

class MusParser(CfgParser):
    extension = 'mus'

    def __init__(self, filepath: Path, tokens: list[Token] = None, logger: Logger = get_logger(__name__)):
        SwbfTextParser.__init__(self, filepath=filepath, tokens=tokens, logger=logger)


if __name__ == '__main__':
    MusParser.cmd_helper()
