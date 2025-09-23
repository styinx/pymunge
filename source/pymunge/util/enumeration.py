class EnumMeta(type):
    def __new__(mcls, name, bases, namespace):
        annotations = namespace.get('__annotations__', {})
        counter = 0
        enumerators = {}

        # Annotations
        for attr in list(annotations) + [k for k in namespace if not k.startswith('__') and k not in annotations]:

            if attr in annotations:
                typ = annotations[attr]

                if attr in namespace:
                    value = namespace[attr]
                    if isinstance(value, int):
                        counter = max(counter, value + 1)

                else:
                    if typ is str:
                        value = attr
                    elif typ is int:
                        value = counter
                        counter += 1
                    else:
                        raise TypeError(f'Unsupported type {typ} for {attr}')

                    namespace[attr] = value

            else:
                value = namespace[attr]
                if isinstance(value, int):
                    counter = max(counter, value + 1)

            enumerators[attr] = namespace[attr]

        # Alias
        for k, v in list(enumerators.items()):
            if isinstance(v, str):
                if v in enumerators:
                    enumerators[k] = enumerators[v]
                    namespace[k] = enumerators[v]

        cls = super().__new__(mcls, name, bases, namespace)
        cls.enumerators = list(enumerators.items())
        return cls

    def __iter__(cls):
        return iter(cls.enumerators)

    def keys(cls):
        return [k for k, _ in cls.enumerators]

    def vals(cls):
        return [v for _, v in cls.enumerators]


class Enum(metaclass=EnumMeta):
    pass