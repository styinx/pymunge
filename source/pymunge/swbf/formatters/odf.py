from pathlib import Path

from swbf.parsers.odf import OdfParser, Section, Key, Value, Comment
from swbf.formatters.formatter import SwbfFormatter
from swbf.formatters.style import Style, OdfStyle


class OdfFormatter(SwbfFormatter):
    def __init__(self, tree: OdfParser, style: Path):
        SwbfFormatter.__init__(self, style)

        self.tree = tree

    def format(self):
        key_space = 0
        key_spaces = {}

        if self.style.whitespace == Style.Whitespace.UseSpaces:
            whitespace_symbol = ' '
        if self.style.whitespace == Style.Whitespace.UseTabs:
            whitespace_symbol = '\t'
        else:
            whitespace_symbol = ''

        if self.style.odf.comment == OdfStyle.Comment.UseBackSlash:
            comment_symbol = '\\\\'
        elif self.style.odf.comment == OdfStyle.Comment.UseForwardSlash:
            comment_symbol = '//'
        else:
            comment_symbol = ''

        print('\n'.join(map(lambda x: x.text, self.tree.find_all_nested(Comment))))


        for section in self.tree.find_all(Section):
            key_spaces[section.name] = 0
            for key in section.find_all(Key):
                key_space = max(key_space, len(key.name))
                key_spaces[section.name] = max(key_spaces[section.name], len(key.name))

        formatted = ''
        for section in self.tree.find_all(Section):
            formatted += f'[{section.name}]\n'

            for node in section:

                if isinstance(node, Key):
                    if self.style.odf.alignment == OdfStyle.Alignment.AlignOnEqual:
                        formatted += f'{key.name:<{key_space}} = '
                    elif self.style.odf.alignment == OdfStyle.Alignment.AlignOnValue:
                        formatted += f'{key.name:}{"=":<{key_space}}'
                    elif self.style.odf.alignment == OdfStyle.Alignment.AlignOnEqualPerSection:
                        formatted += f'{key.name:<{key_spaces[section.name]}} = '
                    elif self.style.odf.alignment == OdfStyle.Alignment.AlignOnValuePerSection:
                        formatted += f'{key.name:}{"=":<{key_spaces[section.name]}}'
                    else:
                        formatted += f'{key.name} = '

                    for val in key.children:
                        if isinstance(val, Value):
                            formatted += val.value + '\n'
                        else:
                            formatted += '\n'

                elif isinstance(node, Comment):
                    formatted += f'{comment_symbol}{node.text}'

        print('\n'.join(formatted.split('\n')[:10]))
        print(self.tree.file)
