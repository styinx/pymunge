from math import log10

from util.enum import Enum
from util.logging import get_logger, Ansi, ScopedLogger


class Severity(Enum):
    """
    The :class:`Severity` of a diagnostic message determines the relevance.
    """

    Error = 'E'
    Warning = 'W'
    Info = 'I'


class DiagnosticMessageMeta(type):
    """
    The :class:`DiagnosticMessageMeta` class automatically increases the diagnostic code
    for a new type of diagnostic message. In addition the diagnostic message name
    is saved.
    """

    Codes = {Severity.Error: 0, Severity.Warning: 0, Severity.Info: 0}

    def __new__(cls, name, bases, dct):
        severity = dct.get('severity', Severity.Error)
        DiagnosticMessageMeta.Codes[severity] += 1
        dct['code'] = DiagnosticMessageMeta.Codes[severity]
        dct['name'] = cls.__name__

        return super().__new__(cls, name, bases, dct)


class DiagnosticMessage(metaclass=DiagnosticMessageMeta):
    """
    The :class:`DiagnosticMessage` records an issue that occurred during the munge process.
    The :attr:`scope` determines the module or topic in which the issue occurred.
    The :attr:`scope` should be set during the definition of the diagnostic message
    and contain a 3 character wide unique identifier.
    """

    scope = '   '

    def __init__(self, text: str | None = None):
        self.code = self.__class__.code
        self.scope = self.__class__.scope
        self.severity: str = self.__class__.severity
        self.text: str | None = text

    def print(self):
        code_digits = round(log10(DiagnosticMessageMeta.Codes[self.severity])) + 1
        print(f'{self.scope}-{self.severity}-{self.code:0{code_digits}}: {self.text}')


class ErrorMessage(DiagnosticMessage):
    severity = Severity.Error


class WarningMessage(DiagnosticMessage):
    severity = Severity.Warning


class InfoMessage(DiagnosticMessage):
    severity = Severity.Info


class Diagnostic:
    """
    The :class:`Diagnostic` class is used to record diagnostic messages and report them to the user.
    """

    def __init__(self, logger: ScopedLogger = get_logger(__name__)):
        self.logger: ScopedLogger = logger
        self.messages: list[DiagnosticMessage] = []
        self.severeties: dict = {}

        for severity in Severity:
            self.severeties[severity] = 0

    def report(self, message: DiagnosticMessage):
        self.messages.append(message)
        self.severeties[message.severity] += 1

        if message.severity == Severity.Error:
            self.logger.error(message.text)
        elif message.severity == Severity.Warning:
            self.logger.warning(message.text)
        elif message.severity == Severity.Info:
            self.logger.info(message.text)

    def summary(self):
        for m in self.messages:
            m.print()

        s = Ansi.color_fg(Ansi.GreenForeground, 'Diagnostic Summary: \n')
        s += Ansi.color_fg(Ansi.RedForeground, f'{self.severeties[Severity.Error]:3d}' + ' Errors \n')
        s += Ansi.color_fg(Ansi.YellowForeground, f'{self.severeties[Severity.Warning]:3d}' + ' Warnings \n')
        s += Ansi.color_fg(Ansi.CyanForeground, f'{self.severeties[Severity.Info]:3d}' + ' Infos \n')
        print(s)
