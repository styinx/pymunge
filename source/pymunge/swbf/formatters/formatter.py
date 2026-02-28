from argparse import Namespace
from importlib import util
from pathlib import Path

from app.environment import MungeEnvironment as ENV
from swbf.formatters.style import Style
from util.diagnostic import ErrorMessage


class IncompleteFormatConfiguration(ErrorMessage):
    def __init__(self):
        super().__init__('Incomplete format configuration')


class SwbfFormatter:
    def __init__(self, style: Path):
        try:
            spec = util.spec_from_file_location(style.stem, style)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)

        except:
            ENV.Diag.report(ErrorMessage('Could not import style file'))

        if not hasattr(module, 'style'):
            raise RuntimeError('Script must define a "style" variable')

        def dict_to_ns(d: dict):
            ns = Namespace()
            for k, v in d.items():
                if isinstance(v, dict):
                    setattr(ns, k, dict_to_ns(v))
                else:
                    setattr(ns, k, v)
            return ns

        self.style = dict_to_ns(module.style)

        self.configure()

    def configure(self):
        if self.style.whitespace == Style.Whitespace.UseSpaces:
            self.whitespace_symbol = ' '
        if self.style.whitespace == Style.Whitespace.UseTabs:
            self.whitespace_symbol = '\t'
        else:
            ENV.Diag.report(IncompleteFormatConfiguration())