import io
from pathlib import Path
import sys
from logging import Logger

from parxel.lexer import Lexer
from parxel.nodes import Document
from parxel.parser import BinaryParser, TextParser
from parxel.token import Token

from app.environment import MungeEnvironment
from app.diagnostic import ErrorMessage
from app.registry import Dependency
from util.logging import get_logger

logger = get_logger(__name__)


class SwbfParser:
    filetype = ''

    def __init__(self, logger: Logger = get_logger(__name__)) -> None:
        self.logger: Logger = logger

    def register_dependency(self, dependency: Dependency):
        if dependency.filepath:
            MungeEnvironment.Registry.lookup['premunge'][dependency.filepath.name] = dependency
            self.logger.debug(f'Add dependency: {dependency.filepath}')

    @classmethod
    def cmd_helper(cls: type):
        # Stub
        MungeEnvironment(get_logger(__name__))

        if len(sys.argv) == 2:
            if not isinstance(sys.argv[0], io.TextIOWrapper):

                path = Path(sys.argv[1])
                if path.is_file():
                    parser = cls(filepath=path)
                    parser.parse()
                    print(parser.dump())

                elif path.is_dir():
                    for file in path.rglob(f'*.{cls.filetype}'):
                        print(file)
                        req = cls(filepath=file)
                        req.parse()

            else:
                lex = Lexer(sys.stdin)
                tokens = lex.tokenize()
                parser = cls(filepath='', tokens=tokens)
                parser.parse()
                print(parser.dump())

        else:
            sys.exit(1)

        # TODO: Global exit code
        sys.exit(0)


class SwbfTextParser(Document, TextParser, SwbfParser):

    class UnrecognizedToken(ErrorMessage):
        def __init__(self, received: str, expected: str):
            super().__init__(f'Unexpected token {received}, expected {expected}')

    def __init__(self, filepath: Path, tokens: list[Token] = None, logger: Logger = get_logger(__name__)):

        SwbfParser.__init__(self, logger=logger)
        Document.__init__(self, filepath=filepath)
        TextParser.__init__(self, filepath=filepath, tokens=tokens, logger=logger)

    def parse_format(self):
        raise NotImplementedError('This is an abstract base class!')


class SwbfBinaryParser(Document, BinaryParser, SwbfParser):

    def __init__(self, filepath: Path, buffer: bytes = None, logger: Logger = get_logger(__name__)):

        SwbfParser.__init__(self,)
        Document.__init__(self, filepath=filepath)
        BinaryParser.__init__(self, buffer=buffer, filepath=filepath, logger=logger)

    def parse_format(self):
        raise NotImplementedError('This is an abstract base class!')

