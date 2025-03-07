class EnumMeta(type):
    Undefined = 'Undefined'

    def __iter__(klass: type):
        return iter([v for k, v in klass.__dict__.items() if k[-1] != '_'])


class Enum(metaclass=EnumMeta):
    Undefined = 'Undefined'
