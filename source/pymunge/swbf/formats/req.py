import re
import sys
from pathlib import Path
from io import FileIO, StringIO
from parxel.lexer import Lexer
from parxel.parser import Parser
from parxel.nodes import Node, Document, LexicalNode
from parxel.token import TK, Token
from util.logging import get_logger
from util.enum import Enum


logger = get_logger(__name__)


class Comment(LexicalNode):
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.text: str = self.raw().strip()


class Condition(LexicalNode):
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        condition = self.raw().strip().split(' ')

        self.name: str = condition[0]
        self.arguments: list[str] = condition[1:]


class Block(LexicalNode):
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.header: str = self.raw().strip()
        self.type: str = ''

        if self.header not in REQ.Header:
            logger.warning(f'Block header "{self.header}" is not known.')


class Type(LexicalNode):

    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.type: str = self.raw().strip()

        if self.type not in REQ.Type:
            logger.warning(f'Block type "{self.type}" is not known.')


class Property(LexicalNode):
    RE = re.compile(r'(.*)=(.*)')

    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        match = re.match(Property.RE, self.raw())

        self.key: str = match.group(1)
        self.value: str = match.group(2)

        if self.key not in REQ.Property:
            logger.warning(f'Block property "{self.key}" is not known.')


class Value(LexicalNode):
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.value: str = self.raw().strip()


class REQ(Document, Parser):
    class Header(Enum):
        Reqn = 'REQN'
        Ucft = 'ucft'

    class Property(Enum):
        Align = 'align'
        Platform = 'platform'

    class Type(Enum):
        Bin = 'bin'
        Bnk = 'bnk'
        Boundary = 'boundary'
        Config = 'config'
        Congraph = 'congraph'
        Class = 'class'
        Envfx = 'envfx'
        Loc = 'loc'
        Lvl = 'lvl'
        Model = 'model'
        Path = 'path'
        Prop = 'prop'
        Script = 'script'
        Str = 'str'
        Terrain = 'terrain'
        Texture = 'texture'
        World = 'world'
        Zaabin = 'zaabin'
        Zafbin = 'zafbin'

    def __init__(self, filepath: Path, tokens: list[Token]):
        Document.__init__(self, filepath=filepath)
        Parser.__init__(self, filepath=filepath, tokens=tokens)

    def parse_format(self):
        while self:
            if self.get().type in TK.Whitespaces:
                self.discard()  # Discard whitespaces

            # Comment
            elif self.get().type == TK.Minus:
                self.consume_strict(TK.Minus)

                self.consume_until(TK.LineFeed)

                comment = Comment(self.collect_tokens())
                self.add_to_scope(comment)

                self.discard()  # \n

            # Begin Block
            elif self.get().type == TK.CurlyBracketOpen:
                self.discard()  # {

            # End Block
            elif self.get().type == TK.CurlyBracketClose:
                self.discard()  # }

                self.exit_scope()

            # Type, Property, Value
            elif self.get().type == TK.QuotationMark:
                self.discard()  # "

                self.consume_until_any([TK.EqualSign, TK.QuotationMark])

                if self.get().type == TK.QuotationMark:

                    if isinstance(self.scope, Block) and len(self.scope.children) == 0:
                        type = Type(self.collect_tokens())
                        self.add_to_scope(type)

                    else:
                        value = Value(self.collect_tokens())
                        self.add_to_scope(value)

                elif self.get().type == TK.EqualSign:
                    self.consume_until(TK.QuotationMark)

                    property = Property(self.collect_tokens())
                    self.add_to_scope(property)

                else:
                    self.error()

                self.discard()  # "

            # Header
            elif self.get().type == TK.Word:
                self.consume(TK.Word)

                block = Block(self.collect_tokens())
                self.enter_scope(block)

            # Condition
            elif self.get().type == TK.NumberSign:
                self.discard()  # #

                # Condition name
                self.consume(TK.Word)
                self.consume_while_any(TK.Whitespaces)

                # Condition parameters
                while self.get().type == TK.Word:
                    self.consume(TK.Word)
                    self.consume_while_any(TK.Whitespaces)
                
                if isinstance(self.scope, Condition):
                    self.collect_tokens() # Discard end of condition
                    self.exit_scope()
                else:
                    condition = Condition(self.collect_tokens())
                    self.enter_scope(condition)

            # Either skip or thow error
            else:
                logger.warning(f'Unrecognized token "{self.get()} ({req.tokens()})".')
                self.discard()
                # self.error(TK.Null)

        return self


if __name__ == '__main__':
    if len(sys.argv) == 2:
        path = Path(sys.argv[1])
        if path.is_file():
            req = REQ.read(filepath=path)
            req.print()
        else:
            for file in path.rglob('*.req'):
                req = REQ.read(filepath=file)

    elif len(sys.argv) > 2:
        req = REQ.read(stream=sys.stdin)
    else:
        sys.exit(1)

    # TODO: Global exit code
    sys.exit(0)
