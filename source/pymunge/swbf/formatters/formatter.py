from importlib import util
from pathlib import Path
from types import SimpleNamespace

from app.environment import MungeEnvironment as ENV
from swbf.parsers.parser import TextParser
from swbf.formatters.style import Style
from util.diagnostic import ErrorMessage
from util.string import BufferedString


class IncompleteFormatConfiguration(ErrorMessage):
    def __init__(self):
        super().__init__('Incomplete format configuration')


class SwbfFormatter:
    def __init__(self, tree: TextParser, style: Path):
        self.style = self.load_style(style)
        self.configure_style()

        self.tree : TextParser = tree
        self.formatted = BufferedString()

    @staticmethod
    def load_style(file: Path):
        try:
            spec = util.spec_from_file_location(file.stem, file)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)

        except:
            ENV.Diag.report(ErrorMessage('Could not import style file'))

        if not hasattr(module, 'style'):
            raise RuntimeError('Script must define a "style" variable')

        def dict_to_ns(d: dict):
            ns = SimpleNamespace()
            for k, v in d.items():
                if isinstance(v, dict):
                    setattr(ns, k, dict_to_ns(v))
                else:
                    setattr(ns, k, v)
            return ns

        return dict_to_ns(module.style)

    def configure_style(self):
        self.trailing_comment_space: str = ' ' * self.style.trailingCommentSpace or 2
        self.indent_space: str = ' ' * (self.style.indentSpace or 2)
        self.keep_empty_lines: int = self.style.keepEmptyLines or 1

        match self.style.whitespace:
            case Style.Whitespace.UseSpaces:
                self.whitespace_symbol = ' '
            case Style.Whitespace.UseTabs:
                self.whitespace_symbol = '\t'
            case _:
                ENV.Diag.report(IncompleteFormatConfiguration())
