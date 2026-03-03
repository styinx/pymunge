from pathlib import Path

from app.environment import MungeEnvironment as ENV
from swbf.parsers.cfg import CfgParser, Block, Call, Comment, Number, String
from swbf.formatters.formatter import SwbfFormatter, IncompleteFormatConfiguration
from swbf.formatters.style import Style, CfgStyle


class CfgFormatter(SwbfFormatter):
    def __init__(self, tree: CfgParser, style: Path):
        SwbfFormatter.__init__(self, tree, style)

        self.configure_cfg_style()

    def configure_cfg_style(self):
        match self.style.cfg.comment:
            case CfgStyle.Comment.UseForwardSlash:
                self.comment_symbol = '//'
            case CfgStyle.Comment.UseDoubleDash:
                self.comment_symbol = '--'
            case _:
                ENV.Diag.report(IncompleteFormatConfiguration())
        
        self.indent = 0
        self.indentSpace = ' ' * (self.style.indentSpace or 2)

    def format_comment(self, comment):
        self.formatted += f'{self.comment_symbol}{comment.text}'

    def format_node(self, node):
        indent = self.indent_space * self.indent
        self.formatted += f'{indent}'

        if isinstance(node, Call):
            self.formatted += f'{node.name}({", ".join([str(x.value) if isinstance(x, Number) else f'"{x.value}"' for x in node.children])})\n'

        elif isinstance(node, Block):
            self.formatted += '{\n'
            self.indent += 1
            for child in node:
                self.format_node(child)
            self.indent -= 1
            self.formatted += f'{indent}}}\n\n'

        elif isinstance(node, Comment):
            self.format_comment(node)

    def format(self) -> str:
        for node in self.tree:
            self.format_node(node)

        return self.formatted.getvalue()

