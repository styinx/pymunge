from logging import Logger
from pathlib import Path
import sys

from parxel.lexer import Lexer
from parxel.nodes import Node, LexicalNode
from parxel.token import TK, Token

from app.environment import MungeEnvironment as ENV
from app.registry import Dependency
from swbf.parsers.parser import SwbfTextParser
from util.diagnostic import WarningMessage
from util.logging import get_logger
from util.enum import Enum


class ConfigWarning(WarningMessage):
    scope = 'CFG'


class Call(LexicalNode):

    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.name: str = self.raw().strip()
        self.is_block: bool = False


class Comment(LexicalNode):

    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.value: str = self.raw().strip()


class String(LexicalNode):

    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.value: str = self.raw().strip()


class Number(LexicalNode):

    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.value: float = float(self.raw().strip())


class CfgParser(SwbfTextParser):
    extension = 'cfg'

    def __init__(self, filepath: Path, tokens: list[Token] = None, logger: Logger = get_logger(__name__)):
        SwbfTextParser.__init__(self, filepath=filepath, tokens=tokens, logger=logger)

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

            # Call
            elif self.get().type == TK.Word:
                self.consume_until(TK.ParanthesisOpen)

                call = Call(self.collect_tokens())
                self.add_to_scope(call)

                self.discard() # (

                self.consume_until_any([TK.QuotationMark, TK.Number, TK.Minus] + [TK.ParanthesisClose])

                while self.get().type != TK.ParanthesisClose:

                    while self.get().type in [TK.QuotationMark, TK.Number, TK.Minus]:

                        # String argument
                        if self.get().type == TK.QuotationMark:
                            self.discard() # "

                            self.consume_until(TK.QuotationMark)

                            arg = String(self.collect_tokens())
                            call.add(arg)

                            self.discard() # "

                        # Number argument
                        elif self.get().type in [TK.Number, TK.Minus]:
                            self.consume_while_any([TK.Number, TK.Period, TK.Minus])

                            arg = Number(self.collect_tokens())
                            call.add(arg)

                    self.discard_while_any(TK.Whitespaces + [TK.Comma])

                self.discard() # )
                
                self.discard_while_any(TK.Whitespaces + [TK.Semicolon])
            
                # Scope enter
                if self.consume(TK.CurlyBracketOpen):
                    self.discard() # {
                    self.enter_scope(call)
                    call.is_block = True

            # Scope exit
            elif self.get().type == TK.CurlyBracketClose:
                self.discard() # }
                self.exit_scope()

            # Either skip or throw error
            else:
                ENV.Diag.report(SwbfTextParser.UnrecognizedToken(self))
                self.discard()
                # self.error(TK.Null)

        return self


if __name__ == '__main__':
    CfgParser.cmd_helper()
