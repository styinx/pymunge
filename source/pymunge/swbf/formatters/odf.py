from pathlib import Path

from app.environment import MungeEnvironment as ENV
from swbf.parsers.odf import OdfParser, Section, Key, Value, Comment, Reference
from swbf.formatters.formatter import SwbfFormatter, IncompleteFormatConfiguration
from swbf.formatters.style import Style, OdfStyle


class OdfFormatter(SwbfFormatter):
    def __init__(self, tree: OdfParser, style: Path):
        SwbfFormatter.__init__(self, tree, style)

        self.configure_odf_style()

    def configure_odf_style(self):
        match self.style.odf.comment:
            case OdfStyle.Comment.UseBackSlash:
                self.comment_symbol = '\\\\'
            case OdfStyle.Comment.UseForwardSlash:
                self.comment_symbol = '//'
            case _:
                ENV.Diag.report(IncompleteFormatConfiguration())

        self.key_space = 0
        self.val_space = 0
        self.key_spaces = {}
        self.val_spaces = {}

        for section in self.tree.find_all(Section):
            self.key_spaces[section.name] = 0
            self.val_spaces[section.name] = 0

            for key in section.find_all(Key):
                self.key_space = max(self.key_space, len(key.name))
                self.key_spaces[section.name] = max(self.key_spaces[section.name], len(key.name))

                space = len(key.children[0].raw().strip())
                self.val_space = max(self.val_space, space)
                self.val_spaces[section.name] = max(self.val_spaces[section.name], space)


    def format_comment(self, comment):
        self.formatted += f'{self.comment_symbol}{comment.text}'

    def format_key(self, key, section):
        if self.style.odf.separateSubsections and key.name in OdfParser.SubSection:
            prefix = '\n'
        else:
            prefix = ''

        match self.style.odf.alignment:
            case OdfStyle.Alignment.AlignOnEqual:
                self.formatted += f'{prefix}{key.name:<{self.key_space}} ='
            case OdfStyle.Alignment.AlignOnValue:
                self.formatted += f'{prefix}{key.name:}{"=":<{self.key_space}}'
            case OdfStyle.Alignment.AlignOnEqualPerSection:
                self.formatted += f'{prefix}{key.name:<{self.key_spaces[section.name]}} = '
            case OdfStyle.Alignment.AlignOnValuePerSection:
                self.formatted += f'{prefix}{key.name:}{"=":<{self.key_spaces[section.name]}}'
            case _:
                self.formatted += f'{prefix}{key.name} = '

    def format_node(self, node, section):
        if isinstance(node, Key):
            self.format_key(node, section)

            for child in node:
                self.format_node(child, section)
            
        elif isinstance(node, Value):
            self.formatted += node.value

        elif isinstance(node, Reference):
            self.formatted += node.filepath

        elif isinstance(node, Comment):
            space = len(node.parent.children[0].raw().strip())

            match self.style.odf.commentAlignment:
                case OdfStyle.CommentAlignment.AlignTrailingComments:
                    self.formatted += ' ' * (self.val_space - space)
                case OdfStyle.CommentAlignment.AlignTrailingCommentsPerSection:
                    self.formatted += ' ' * (self.val_spaces[section.name] - space)
                case _:
                    self.formatted += self.trailing_comment_space
            self.format_comment(node)

    def format_section(self, section):
        for node in section:
            if isinstance(node, Comment):
                self.format_comment(node)
            else:
                self.format_node(node, section)

            self.formatted += '\n'

        self.formatted += '\n'

    def format(self) -> str:
        for node in self.tree:
            if isinstance(node, Section):
                self.formatted += f'[{node.name}]\n'
                self.format_section(node)
            elif isinstance(node, Comment):
                self.format_comment(node)

        return self.formatted.getvalue()

