import io
from pathlib import Path
import sys
from logging import Logger

from parxel.lexer import Lexer
from parxel.nodes import Document
from parxel.parser import BinaryParser, TextParser
from parxel.token import Token

from app.registry import FileRegistry, Dependency
from util.logging import get_logger

logger = get_logger(__name__)


class Format:
    def __init__(self, registry: FileRegistry, logger: Logger = logger) -> None:
        self.registry = registry
        self.logger = logger

    def register_dependency(self, dependency: Dependency):
        if dependency.filepath:
            self.registry.lookup['premunge'][dependency.filepath.name] = dependency
            self.logger.debug(f'Add dependency: {dependency.filepath}')

    @classmethod
    def cmd_helper(cls: type):
        if len(sys.argv) == 2:
            if not isinstance(sys.argv[0], io.TextIOWrapper):

                path = Path(sys.argv[1])
                if path.is_file():
                    parser = cls(filepath=path, registry=FileRegistry())
                    parser.parse()
                    print(parser.dump())

                elif path.is_dir():
                    for file in path.rglob(f'*.{cls.__name__.lower()}'):
                        print(file)
                        req = cls(filepath=file, registry=FileRegistry())
                        req.parse()

            else:
                lex = Lexer(sys.stdin)
                tokens = lex.tokenize()
                parser = cls(filepath='', tokens=tokens, registry=FileRegistry())
                parser.parse()
                print(parser.dump())

        else:
            sys.exit(1)

        # TODO: Global exit code
        sys.exit(0)


class TextFormat(Document, TextParser, Format):

    def __init__(self, registry: FileRegistry, filepath: Path, tokens: list[Token] = None, logger: Logger = logger):

        Format.__init__(self, registry=registry, logger=logger)
        Document.__init__(self, filepath=filepath)
        TextParser.__init__(self, filepath=filepath, tokens=tokens, logger=logger)

    def parse_format(self):
        raise NotImplementedError('This is an abstract base class!')

    def register_dependency(self, dependency: Dependency):
        if dependency.filepath:
            self.registry.lookup['premunge'][dependency.filepath.name] = dependency
            logger.debug(f'Add dependency: {dependency.filepath}')


class BinaryFormat(Document, BinaryParser, Format):

    def __init__(self, registry: FileRegistry, filepath: Path, buffer: bytes = None, logger: Logger = logger):

        Format.__init__(self, registry=registry)
        Document.__init__(self, filepath=filepath)
        BinaryParser.__init__(self, buffer=buffer, filepath=filepath, logger=logger)

    def parse_format(self):
        raise NotImplementedError('This is an abstract base class!')

