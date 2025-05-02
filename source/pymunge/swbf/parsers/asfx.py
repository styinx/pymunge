from pathlib import Path
import sys

from parxel.lexer import Lexer
from parxel.nodes import Node, LexicalNode
from parxel.token import TK, Token

from app.registry import FileRegistry, Dependency
from swbf.parsers.format import Format
from util.logging import get_logger
from util.enum import Enum


logger = get_logger(__name__)


class Comment(LexicalNode):
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.value: str = self.raw().strip()


class Condition(LexicalNode):
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        condition = self.raw().strip().split(' ')

        self.name: str = condition[0]
        self.arguments: list[str] = condition[1:]


class SoundEffect(LexicalNode, Dependency):
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        values: list[str] = self.raw().strip().split(' ')

        self.path: str = values[0]
        self.name: str = '' if len(values) == 1 else values[1]

        filepath = Path(self.path)
        Dependency.__init__(self, filepath.resolve())


class Switch(LexicalNode):
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.value: str = self.raw().strip()

        if self.value not in Asfx.Switch:
            logger.warning(f'Switch "{self.value}" is not known.')


class Config(LexicalNode):
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.value: str = self.raw().strip()

        if self.value not in Asfx.Config:
            logger.warning(f'Config "{self.value}" is not known.')

        #elif self.value not in Asfx.SwitchConfigValue[self.parent.value]:
        #    logger.warning(f'Config "{self.value}" is not a valid config for {self.parent.value}.')


class Value(LexicalNode):
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.value: str = self.raw().strip()

        if self.value not in Asfx.Value:
            logger.warning(f'Value "{self.value}" is not known.')

        #elif self.value not in Asfx.SwitchConfigValue[self.parent.parent.value][self.parent.value]:
        #    logger.warning(f'Value "{self.value}" is not a valid value for config {self.parent.value}.')


class Asfx(Format):
    class Switch(Enum):
        Resample = 'resample'

    class Config(Enum):
        Pc = 'pc'
        Ps2 = 'ps2'
        Xbox = 'xbox'

    class Value(Enum):
        _320 = '320'
        _16000 = '16000'
        _20000 = '20000'
        _22050 = '22050'
        _44100 = '44100'

    SwitchConfigValue = {
        Switch.Resample : {
            Config.Pc : [Value._22050, Value._44100],
            Config.Ps2 : [Value._22050, Value._44100]
        }
    }

    def __init__(self, registry : FileRegistry, filepath: Path, tokens: list[Token] = None, logger = logger):
        Format.__init__(self, registry=registry, filepath=filepath, tokens=tokens, logger=logger)

    def parse_format(self):
        while self:
            if self.get().type in TK.Whitespaces:
                self.discard()  # Discard whitespaces

            # Comment
            elif self.get().type == TK.Slash:
                self.consume_strict(TK.Slash)

                self.consume_until(TK.LineFeed)

                comment = Comment(self.collect_tokens())
                self.add_to_scope(comment)

            # Sound
            elif self.get().type == TK.Word:
                self.consume_until_any(TK.Whitespaces)

                self.consume_while_any(TK.Whitespaces)

                if self.get().type == TK.Word:
                    self.next()

                    self.consume_while_any(TK.Whitespaces)

                sfx = SoundEffect(self.collect_tokens())
                self.enter_scope(sfx)
                self.register_dependency(value)

                while self.get().type == TK.Minus:
                    self.discard() # -

                    self.consume_strict(TK.Word)

                    switch = Switch(self.collect_tokens())
                    self.enter_scope(switch)

                    self.consume_until(TK.Word)

                    while self.get().type not in [TK.Minus, TK.LineFeed]:
                        self.consume_strict(TK.Word)

                        config = Config(self.collect_tokens())
                        self.enter_scope(config)

                        self.consume_until(TK.Number)

                        self.consume(TK.Number)

                        value = Value(self.collect_tokens())
                        self.add_to_scope(value)

                        self.exit_scope()

                        self.consume_until_any(TK.Whitespaces)

                    self.exit_scope()

                self.exit_scope()

            # Condition
            elif self.get().type == TK.NumberSign:
                self.discard()  # #

                # Condition name
                self.consume_strict(TK.Word)
                self.consume_until(TK.Word)

                # Condition parameters
                while self.get().type == TK.Word:
                    self.consume_strict(TK.Word)
                    self.consume_while_any(TK.Space)

                if isinstance(self.scope, Condition):
                    self.collect_tokens() # Discard end of condition
                    self.exit_scope()
                else:
                    condition = Condition(self.collect_tokens())
                    self.enter_scope(condition)

            # Either skip or throw error
            else:
                logger.warning(f'Unrecognized token at position {self.pos}: "{self.get()} ({self.tokens()})".')
                self.discard()
                # self.error(TK.Null)

        return self


if __name__ == '__main__':
    if len(sys.argv) == 2:
        path = Path(sys.argv[1])
        if path.is_file():
            asfx = Asfx.read(filepath=path)
            asfx.print()
        else:
            for file in path.rglob('*.asfx'):
                try:
                    asfx = Asfx.read(filepath=file)
                except Lexer.EmptyStreamException:
                    pass

    elif len(sys.argv) > 2:
        asfx = Asfx.read(stream=sys.stdin)
    else:
        sys.exit(1)

    # TODO: Global exit code
    sys.exit(0)
