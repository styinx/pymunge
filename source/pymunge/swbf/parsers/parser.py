import io
from pathlib import Path
import sys

from parxel.lexer import Lexer
from parxel.nodes import Document
from parxel.parser import BinaryParser, TextParser
from parxel.token import Token

from app.environment import MungeEnvironment as ENV
from util.diagnostic import ErrorMessage
from util.logging import get_logger, ScopedLogger

logger = get_logger(__name__)


class SwbfParser(Document):
    Extension = ''

    def __init__(self, filepath: Path, logger: ScopedLogger = get_logger(__name__)) -> None:
        Document.__init__(self, filepath=filepath)

        self.logger: ScopedLogger = logger

        ENV.Reg.register_file(self.filepath)

    @classmethod
    def cmd_helper(cls: type):
        # Stub
        ENV(get_logger(__name__))

        if len(sys.argv) == 2:
            if not isinstance(sys.argv[0], io.TextIOWrapper):

                path = Path(sys.argv[1])
                if path.is_file():
                    parser = cls(filepath=path)
                    parser.parse()
                    print(parser.dump(recursive=True))

                elif path.is_dir():
                    for file in path.rglob(f'*.{cls.Extension}'):
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


class SwbfTextParser(TextParser, SwbfParser):

    class UnexpectedToken(ErrorMessage):
        TOPIC = 'PAR'

        def __init__(self, parser: TextParser, received: str, expected: str):
            super().__init__(f'Unexpected token at position {parser.token_position()}: Got "{received}", expected "{expected}"')

    class UnrecognizedToken(ErrorMessage):
        TOPIC = 'PAR'

        def __init__(self, parser: TextParser):
            super().__init__(f'Unrecognized token at position {parser.token_position()}: "{parser.get()} ({parser.get().type}) ({parser.tokens()})".')

    def __init__(self, filepath: Path, tokens: list[Token] | None = None, logger: ScopedLogger = get_logger(__name__)):

        SwbfParser.__init__(self, filepath=filepath, logger=logger)
        Document.__init__(self, filepath=filepath)
        TextParser.__init__(self, filepath=filepath, tokens=tokens, logger=logger)

    def parse_format(self):
        raise NotImplementedError('This is an abstract base class!')


class SwbfBinaryParser(BinaryParser, SwbfParser):

    def __init__(self, filepath: Path, buffer: bytes | None = None, logger: ScopedLogger = get_logger(__name__)):

        SwbfParser.__init__(self, filepath=filepath, logger=logger)
        Document.__init__(self, filepath=filepath)
        BinaryParser.__init__(self, filepath=filepath, buffer=buffer, logger=logger)

    def parse_format(self):
        raise NotImplementedError('This is an abstract base class!')
