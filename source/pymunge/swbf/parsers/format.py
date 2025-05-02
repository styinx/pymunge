import io
from pathlib import Path
import sys

from parxel.lexer import Lexer
from parxel.nodes import Document
from parxel.parser import TextParser
from parxel.token import Token

from app.registry import FileRegistry, Dependency
from util.logging import get_logger


logger = get_logger(__name__)


class Format(Document, TextParser):
    def __init__(self, registry: FileRegistry, filepath: Path, tokens: list[Token] = None, logger = logger):
        self.registry: FileRegistry = registry

        Document.__init__(self, filepath=filepath)
        TextParser.__init__(self, filepath=filepath, tokens=tokens, logger=logger)

    def parse_format(self):
        raise NotImplementedError('This is an abstract base class!')

    def register_dependency(self, dependency: Dependency):
        if dependency.filepath:
            self.registry.lookup['premunge'][dependency.filepath.name] = dependency
            print(dependency.filepath)

    @classmethod
    def cmd_helper(cls: type):
        if len(sys.argv) == 2:
            if not isinstance(sys.argv[0], io.TextIOWrapper):

                path = Path(sys.argv[1])
                if path.is_file():
                    req = cls(filepath=path, registry=FileRegistry())
                    req.parse()
                    req.print()

                elif path.is_dir():
                    for file in path.rglob(f'*.{cls.__name__.lower()}'):
                        print(file)
                        req = cls(filepath=file, registry=FileRegistry())
                        req.parse()

            else:
                lex = Lexer(sys.stdin)
                tokens = lex.tokenize()
                req = cls(filepath='', tokens=tokens, registry=FileRegistry())
                req.parse()
                req.print()

        else:
            sys.exit(1)

        # TODO: Global exit code
        sys.exit(0)
