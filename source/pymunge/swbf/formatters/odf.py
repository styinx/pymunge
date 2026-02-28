from pathlib import Path

from app.environment import MungeEnvironment as ENV
from swbf.parsers.odf import OdfParser, Section, Key, Value, Comment, Reference
from swbf.formatters.formatter import SwbfFormatter, IncompleteFormatConfiguration
from swbf.formatters.style import Style, OdfStyle
from util.diagnostic import ErrorMessage
from util.string import BufferedString


class OdfFormatter(SwbfFormatter):
    def __init__(self, tree: OdfParser, style: Path):
        SwbfFormatter.__init__(self, style)

        self.configure()

        self.tree = tree
        self.formatted = BufferedString()

        self.key_space = 0
        self.key_spaces = {}

        for section in self.tree.find_all(Section):
            self.key_spaces[section.name] = 0
            for key in section.find_all(Key):
                self.key_space = max(self.key_space, len(key.name))
                self.key_spaces[section.name] = max(self.key_spaces[section.name], len(key.name))

    def configure(self):
        if self.style.odf.comment == OdfStyle.Comment.UseBackSlash:
            self.comment_symbol = '\\\\'
        elif self.style.odf.comment == OdfStyle.Comment.UseForwardSlash:
            self.comment_symbol = '//'
        else:
            ENV.Diag.report(IncompleteFormatConfiguration())

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
            self.format_comment(node)

    def format_section(self, section):
        for node in section:
            if isinstance(node, Comment):
                self.format_comment(node)
            else:
                self.format_node(node, section)

            self.formatted += '\n'

        self.formatted += '\n'

    def format(self):
        for node in self.tree:
            if isinstance(node, Section):
                self.formatted += f'[{node.name}]\n'
                self.format_section(node)
            elif isinstance(node, Comment):
                self.format_comment(node)

        #print(self.tree.file)
        #print('\n'.join(formatted.split('\n')[:]))
        print(self.formatted.getvalue())

