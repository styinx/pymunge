import sys
from pathlib import Path
from parxel.parser import Parser
from parxel.nodes import Node, Document, LexicalNode
from parxel.token import TK, Token
from util.logging import get_logger
from util.enum import Enum


logger = get_logger(__name__)


class SoundPath(LexicalNode):
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.value: str = self.raw().strip()


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
        
        elif self.value not in Asfx.SwitchConfigValue[self.parent.value]:
            logger.warning(f'Config "{self.value}" is not a valid config for {self.parent.value}.')


class Value(LexicalNode):
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.value: str = self.raw().strip()

        if self.value not in Asfx.Value:
            logger.warning(f'Value "{self.value}" is not known.')

        elif self.value not in Asfx.SwitchConfigValue[self.parent.parent.value][self.parent.value]:
            logger.warning(f'Value "{self.value}" is not a valid value for config {self.parent.value}.')


class Asfx(Document, Parser):
    class Switch(Enum):
        Resample = 'resample'

    class Config(Enum):
        Pc = 'pc'
        Ps2 = 'ps2'

    class Value(Enum):
        _22050 = '22050'
    
    SwitchConfigValue = {
        Switch.Resample : {
            Config.Pc : [Value._22050],
            Config.Ps2 : [Value._22050]
        }
    }

    def __init__(self, filepath: Path, tokens: list[Token]):
        Document.__init__(self, filepath=filepath)
        Parser.__init__(self, filepath=filepath, tokens=tokens)

    def parse_format(self):
        while self:
            if self.get().type in TK.Whitespaces:
                self.discard()  # Discard whitespaces

            elif self.get().type == TK.Minus: # TODO: Are comments allowed?
                self.discard() # '-'

                self.consume_until_any(TK.Whitespaces)

                switch = Switch(self.collect_tokens())
                self.enter_scope(switch)

                self.discard() # Discard whitespaces

                self.consume_until_any(TK.Whitespaces)

                config = Config(self.collect_tokens(), self.scope)
                self.enter_scope(config)

                self.discard() # Discard whitespaces

                self.consume_until_any(TK.Whitespaces)

                value = Value(self.collect_tokens(), self.scope)
                self.add_to_scope(value)

                self.exit_scope()
                self.exit_scope()
            
            elif self.get().type == TK.Word:
                self.consume_until_any(TK.Whitespaces)

                print(self.tokens())
                path = SoundPath(self.collect_tokens())
                self.add_to_scope(path)

                self.discard() # Discard whitespaces

            # Either skip or throw error
            else:
                logger.warning(f'Unrecognized token "{self.get()} ({self.tokens()})".')
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
            for file in path.rglob('*.option'):
                asfx = Asfx.read(filepath=file)

    elif len(sys.argv) > 2:
        asfx = Asfx.read(stream=sys.stdin)
    else:
        sys.exit(1)

    # TODO: Global exit code
    sys.exit(0)
