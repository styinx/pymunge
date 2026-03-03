from pathlib import Path

from app.environment import MungeEnvironment as ENV
from swbf.parsers.fx import FxParser
from swbf.formatters.cfg import CfgFormatter
from swbf.formatters.style import Style, CfgStyle


class FxFormatter(CfgFormatter):
    def __init__(self, tree: FxParser, style: Path):
        CfgFormatter.__init__(self, tree, style)

        self.configure_fx_style()

    def configure_fx_style(self):
        pass
