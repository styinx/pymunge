import logging
import sys
from pathlib import Path
from util.enum import Enum


class Ansi:
    # yapf: disable
    Styles = [
        Bold,
        Italic,
        Underline
    ] = [1, 3, 4]

    Resets = [
        Reset,
        ResetBold,
        ResetItalic,
        ResetUnderline
    ] = [0, 22, 23, 24]

    ForegroundColors = [
        BlackForeground,
        RedForeground,
        GreenForeground,
        YellowForeground,
        BlueForeground,
        MagentaForeground,
        CyanForeground,
        WhiteForeground,
        GrayForeground,
        DefaultForeground
    ] = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39]

    BackgroundColors = [
        BlackBackground,
        RedBackground,
        GreenBackground,
        YellowBackground,
        BlueBackground,
        MagentaBackground,
        CyanBackground,
        WhiteBackground,
        GrayBackground,
        DefaultBackground
    ] = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]
    # yapf: enable

    Escape = '\x1b[{}m'

    @staticmethod
    def style(set_style: int, reset_style: int, string: str):
        return Ansi.Escape.format(set_style) + string + Ansi.Escape.format(reset_style)

    @staticmethod
    def color_fg(color: int, string: str, reset_color: int = DefaultForeground):
        return Ansi.style(color, reset_color, string)

    @staticmethod
    def color_bg(color: int, string: str, reset_color: int = DefaultBackground):
        return Ansi.style(color, reset_color, string)

    @staticmethod
    def bold(string: str):
        return Ansi.style(Ansi.Bold, Ansi.ResetBold, string)

    @staticmethod
    def italic(string: str):
        return Ansi.style(Ansi.Italic, Ansi.ResetItalic, string)

    @staticmethod
    def underline(string: str):
        return Ansi.style(Ansi.Underline, Ansi.ResetUnderline, string)


class LogLevel(Enum):
    Debug = 'debug'
    Info = 'info'
    Warning = 'warning'
    Error = 'error'
    Critical = 'critical'


class ScopedLogger(logging.LoggerAdapter):

    def __init__(self, logger):
        super().__init__(logger, {})
        self._indent_level = 0
        self._continuation_indent = '• '
        self._initial_indent = '  '

    def __enter__(self):
        self.add()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sub()

    def add(self):
        self._indent_level += 1

    def sub(self):
        self._indent_level -= 1

    def process(self, msg: str, kwargs):
        indent: str = ''
        if self._indent_level > 0:
            indent = self._initial_indent * (self._indent_level - 1)
            indent += self._continuation_indent
        return super().process(indent + msg, kwargs)


class ColorFormatter(logging.Formatter):
    LevelStyle = {
        LogLevel.Debug: (Ansi.GreenForeground, Ansi.Italic),
        LogLevel.Info: (Ansi.CyanForeground, ),
        LogLevel.Warning: (Ansi.YellowForeground, ),
        LogLevel.Error: (Ansi.RedForeground, ),
        LogLevel.Critical: (Ansi.RedForeground, Ansi.Bold),
    }

    def __init__(self, format: str, datefmt: str, *args, **kwargs):
        super().__init__(format, *args, **kwargs)
        self.format_string = format
        self.datefmt = datefmt

    def format(self, record):
        style = ';'.join(list(map(str, ColorFormatter.LevelStyle[record.levelname.lower()])))
        prefix = Ansi.Escape.format(style)
        suffix = Ansi.Escape.format(Ansi.Reset)
        log_format = prefix + self.format_string + suffix
        formatter = logging.Formatter(log_format, datefmt=self.datefmt)
        return formatter.format(record)


def get_logger(name: str, path: Path = Path(), level: str = LogLevel.Info, ansi_style: bool = False):
    logger = logging.getLogger(name)

    datefmt='%Y-%m-%d %H:%M:%S'

    # Stream handler
    # yapf: disable
    stream_format = str(
        '[%(asctime)s.%(msecs)03d]'
        '[%(levelname)-8s]'
        '[%(name)-8s]'
        '[%(filename)s:%(lineno)-d] '
        '%(message)s'
    )
    # yapf: enable

    stream_handler = logging.StreamHandler(sys.stdout)

    if ansi_style:
        stream_handler.setFormatter(ColorFormatter(stream_format, datefmt=datefmt))
    else:
        stream_handler.setFormatter(logging.Formatter(stream_format, datefmt=datefmt))

    logger.addHandler(stream_handler)

    # File handler
    if path.name:
        # yapf: disable
        file_format = str(
            '%(asctime)s.%(msecs)03d | '
            '%(levelname)-8s | '
            '%(name)-8s | '
            '%(filename)s:%(lineno)-d   '
            '%(message)s'
        )
        # yapf: enable

        file_handler = logging.FileHandler(path / (name + '.log'))
        file_handler.setFormatter(logging.Formatter(file_format, datefmt=datefmt))
        logger.addHandler(file_handler)

    logger.setLevel(level.upper())

    return ScopedLogger(logger)
