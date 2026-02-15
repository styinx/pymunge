from pathlib import Path

from app.environment import MungeEnvironment as ENV
from swbf.parsers.odf import OdfParser, Section, Key, Value, Comment, Reference
from swbf.formatters.formatter import SwbfFormatter
from swbf.formatters.style import Style, OdfStyle
from util.diagnostic import ErrorMessage


class IncompleteFormatConfiguration(ErrorMessage):
    def __init__(self):
        super().__init__('Incomplete format configuration')


class OdfFormatter(SwbfFormatter):
    def __init__(self, tree: OdfParser, style: Path):
        SwbfFormatter.__init__(self, style)

        self.tree = tree

        if self.style.whitespace == Style.Whitespace.UseSpaces:
            self.whitespace_symbol = ' '
        elif self.style.whitespace == Style.Whitespace.UseTabs:
            self.whitespace_symbol = '\t'
        else:
            ENV.Diag.report(IncompleteFormatConfiguration())

        if self.style.odf.comment == OdfStyle.Comment.UseBackSlash:
            self.comment_symbol = '\\\\'
        elif self.style.odf.comment == OdfStyle.Comment.UseForwardSlash:
            self.comment_symbol = '//'
        else:
            ENV.Diag.report(IncompleteFormatConfiguration())

        self.key_space = 0
        self.key_spaces = {}

        for section in self.tree.find_all(Section):
            self.key_spaces[section.name] = 0
            for key in section.find_all(Key):
                self.key_space = max(self.key_space, len(key.name))
                self.key_spaces[section.name] = max(self.key_spaces[section.name], len(key.name))

    def format_comment(self, comment):
        return f'{self.comment_symbol}{comment.text}'

    def format_key(self, key, section):
        match self.style.odf.alignment:
            case OdfStyle.Alignment.AlignOnEqual:
                return f'{key.name:<{self.key_space}} ='
            case OdfStyle.Alignment.AlignOnValue:
                return f'{key.name:}{"=":<{self.key_space}}'
            case OdfStyle.Alignment.AlignOnEqualPerSection:
                return f'{key.name:<{self.key_spaces[section.name]}} = '
            case OdfStyle.Alignment.AlignOnValuePerSection:
                return f'{key.name:}{"=":<{self.key_spaces[section.name]}}'
            case _:
                return f'{key.name} = '

    def format_node(self, node, section):
        formatted = ''

        if isinstance(node, Key):
            formatted += self.format_key(node, section)

            for child in node:
                formatted += self.format_node(child, section)
            
            formatted += '\n'

        elif isinstance(node, Value):
            formatted += node.value

        elif isinstance(node, Reference):
            formatted += node.filepath

        elif isinstance(node, Comment):
            formatted += self.format_comment(node)

        return formatted

    def format_section(self, section):
        formatted = ''

        for node in section:
            if isinstance(node, Comment):
                formatted += self.format_comment(node) + '\n'
            else:
                formatted += self.format_node(node, section)

        formatted += '\n'

        return formatted

    def format(self):
        formatted = ''
        for node in self.tree:
            if isinstance(node, Section):
                formatted += f'[{node.name}]\n'
                formatted += self.format_section(node)
            elif isinstance(node, Comment):
                formatted += self.format_comment(node)

        print(self.tree.file)
        #print('\n'.join(formatted.split('\n')[:50]))
        print(formatted)
