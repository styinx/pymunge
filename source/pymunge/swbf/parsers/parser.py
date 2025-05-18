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
    def __init__(self, environment: MungeEnvironment, logger: Logger = logger) -> None:
        self.environment = environment
        self.logger = logger

    def register_dependency(self, dependency: Dependency):
        if dependency.filepath:
            self.environment.registry.lookup['premunge'][dependency.filepath.name] = dependency
            self.logger.debug(f'Add dependency: {dependency.filepath}')

    @classmethod
    def cmd_helper(cls: type):
        if len(sys.argv) == 2:
            if not isinstance(sys.argv[0], io.TextIOWrapper):

                path = Path(sys.argv[1])
                if path.is_file():
                    parser = cls(environment=MungeEnvironment(), filepath=path)
                    parser.parse()
                    print(parser.dump())

                elif path.is_dir():
                    for file in path.rglob(f'*.{cls.__name__.lower()}'):
                        print(file)
                        req = cls(environment=MungeEnvironment(), filepath=file)
                        req.parse()

            else:
                lex = Lexer(sys.stdin)
                tokens = lex.tokenize()
                parser = cls(environment=MungeEnvironment(), filepath='', tokens=tokens)
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

    def __init__(self, environment: MungeEnvironment, filepath: Path, tokens: list[Token] = None, logger: Logger = logger):

        SwbfParser.__init__(self, environment=environment, logger=logger)
        Document.__init__(self, filepath=filepath)
        TextParser.__init__(self, filepath=filepath, tokens=tokens, logger=logger)

    def parse_format(self):
        raise NotImplementedError('This is an abstract base class!')


class SwbfBinaryParser(Document, BinaryParser, SwbfParser):

    def __init__(self, environment: MungeEnvironment, filepath: Path, buffer: bytes = None, logger: Logger = logger):

        SwbfParser.__init__(self, environment=environment)
        Document.__init__(self, filepath=filepath)
        BinaryParser.__init__(self, buffer=buffer, filepath=filepath, logger=logger)

    def parse_format(self):
        raise NotImplementedError('This is an abstract base class!')

