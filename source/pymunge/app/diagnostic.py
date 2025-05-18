from logging import Logger

from util.logging import get_logger


logger = get_logger(__name__)


class Severity:
    Error = 0
    Warning = 1
    Info = 2


class DiagnosticMessageMeta(type):
    Codes = {
        Severity.Error: 0,
        Severity.Warning: 0,
        Severity.Info: 0
    }

    def __new__(cls, name, bases, dct):
        severity = dct.get('severity', Severity.Error)
        DiagnosticMessageMeta.Codes[severity] += 1
        dct['code'] = DiagnosticMessageMeta.Codes[severity]
        dct['name'] = cls.__name__

        return super().__new__(cls, name, bases, dct)


class DiagnosticMessage(metaclass=DiagnosticMessageMeta):
    def __init__(self, text: str = None):
        self.code = self.__class__.code
        self.severity: int = self.__class__.severity
        self.text: str = text


class ErrorMessage(DiagnosticMessage):
    severity = Severity.Error


class WarningMessage(DiagnosticMessage):
    severity = Severity.Warning


class InfoMessage(DiagnosticMessage):
    severity = Severity.Info


class Diagnostic:
    def __init__(self, logger: Logger = logger):
        self.logger: Logger = logger
        self.messages: list[DiagnosticMessage] = []
    
    def report(self, message: DiagnosticMessage):
        self.messages.append(message)
