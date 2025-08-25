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
    Names = []

    def __new__(cls, name, bases, dct):
        severity = dct.get('SEVERITY', Severity.Error)
        DiagnosticMessageMeta.Codes[severity] += 1
        DiagnosticMessageMeta.Names.append(name)
        dct['CODE'] = DiagnosticMessageMeta.Codes[severity]
        dct['NAME'] = name

        return super().__new__(cls, name, bases, dct)


class DiagnosticMessage(metaclass=DiagnosticMessageMeta):
    """
    The :class:`DiagnosticMessage` records an issue that occurred during the munge process.
    The :attr:`TOPIC` determines the module or topic in which the issue occurred.
    The :attr:`SCOPE` should be set during the definition of the diagnostic message
    and contain a 3 character wide unique identifier.
    """

    TOPIC = '   '
    SEVERITY = Severity.Info
    CODE = 0
    NAME = ''

    def __init__(self, text: str | None = None):
        self.text: str | None = text

    def __str__(self):
        code_digits = round(log10(max(0.1, max(DiagnosticMessageMeta.Codes.values()))))
        name_length = len(max(DiagnosticMessageMeta.Names, key=lambda x: len(x)))
        code = self.__class__.CODE
        name = self.__class__.NAME
        severity = self.__class__.SEVERITY
        topic = self.__class__.TOPIC
        triplet = f'{topic}-{severity}-{code:0{code_digits}}'

        message = f'[{triplet}] {name:{name_length}}: {self.text}'
        if severity == Severity.Info:
            return Ansi.color_fg(Ansi.CyanForeground, message)
        elif severity == Severity.Warning:
            return Ansi.color_fg(Ansi.YellowForeground, message)
        elif severity == Severity.Error:
            return Ansi.color_fg(Ansi.RedForeground, message)



class ErrorMessage(DiagnosticMessage):
    SEVERITY = Severity.Error


class WarningMessage(DiagnosticMessage):
    SEVERITY = Severity.Warning


class InfoMessage(DiagnosticMessage):
    SEVERITY = Severity.Info


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
        self.severeties[message.SEVERITY] += 1

        if message.SEVERITY == Severity.Error:
            self.logger.error(str(message))
        elif message.SEVERITY == Severity.Warning:
            self.logger.warning(str(message))
        elif message.SEVERITY == Severity.Info:
            self.logger.info(str(message))

    def details(self):
        print(Ansi.color_fg(Ansi.GreenForeground, '\nDiagnostic Details: \n'))
        for m in self.messages:
            print(m)

    def summary(self):
        s = Ansi.color_fg(Ansi.GreenForeground, '\nDiagnostic Summary: \n')
        s += Ansi.color_fg(Ansi.RedForeground, f'{self.severeties[Severity.Error]:3d}' + ' Errors \n')
        s += Ansi.color_fg(Ansi.YellowForeground, f'{self.severeties[Severity.Warning]:3d}' + ' Warnings \n')
        s += Ansi.color_fg(Ansi.CyanForeground, f'{self.severeties[Severity.Info]:3d}' + ' Infos \n')
        print(s)
