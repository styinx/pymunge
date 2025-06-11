from logging import Logger
from pathlib import Path
import re

from parxel.nodes import Document, LexicalNode, Node
from parxel.token import TK, Token

from app.environment import MungeEnvironment
from app.diagnostic import WarningMessage
from app.registry import Dependency
from swbf.parsers.parser import SwbfTextParser
from util.enum import Enum
from util.logging import get_logger


class ReqWarning(WarningMessage):
    scope = 'REQ'


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

        if self.header not in ReqParser.Header:
            MungeEnvironment.Diagnostic.report(ReqWarning(f'Block header "{self.header}" is not known.'))


class Type(LexicalNode):

    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.type: str = self.raw().strip()

        if self.type not in ReqParser.Type:
            MungeEnvironment.Diagnostic.report(ReqWarning(f'Block type "{self.type}" is not known.'))


class Property(LexicalNode):
    RE = re.compile(r'(.*)=(.*)')

    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        match = re.match(Property.RE, self.raw())

        self.key: str = match.group(1)
        self.value: str = match.group(2)

        if self.key not in ReqParser.Property:
            MungeEnvironment.Diagnostic.report(ReqWarning(f'Block property "{self.key}" is not known.'))


class Value(LexicalNode, Dependency):

    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)
        Dependency.__init__(self, filepath=None)

        self.name: str = self.raw().strip()

        if self.parent.type in ReqParser.TypeFileMapping:
            # TODO: Make document the root
            # filepath = self.root
            def root(node) -> Document:
                if isinstance(node, Document):
                    return node
                elif node.parent:
                    return root(node.parent)
                return None

            ending = ReqParser.TypeFileMapping[self.parent.type]
            self.filepath = (Path(root(self).filepath.parent) / f'{self.name}.{ending}').resolve()


class ReqParser(SwbfTextParser):
    filetype = 'req'

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

    TypeFileMapping = {
        Type.Bnk: 'asfx',  # TODO sfx
        Type.Class: 'odf',
        Type.Config: 'snd',
        Type.Lvl: 'req',
        Type.Model: 'msh',
        Type.World: 'wld'
    }

    def __init__(self, filepath: Path, tokens: list[Token] = None, logger: Logger = get_logger(__name__)):
        SwbfTextParser.__init__(self, filepath=filepath, tokens=tokens, logger=logger)

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
                        value = Value(self.collect_tokens(), type)
                        self.add_to_scope(value)
                        self.register_dependency(value)

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
                self.consume_strict(TK.Word)
                self.consume_while_any(TK.Whitespaces)

                # Condition parameters
                while self.get().type == TK.Word:
                    self.consume(TK.Word)
                    self.consume_while_any(TK.Whitespaces)

                if isinstance(self.scope, Condition):
                    self.collect_tokens()  # Discard end of condition
                    self.exit_scope()
                else:
                    condition = Condition(self.collect_tokens())
                    self.enter_scope(condition)

            # Either skip or throw error
            else:
                self.logger.warning(f'Unrecognized token "{self.get()} ({self.tokens()})".')
                self.discard()
                # self.error(TK.Null)

        return self


if __name__ == '__main__':
    ReqParser.cmd_helper()
