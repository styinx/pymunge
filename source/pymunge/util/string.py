from io import StringIO

class BufferedString(StringIO):
    def __init__(self, initial_value = "", newline = "\n"):
        super().__init__(initial_value, newline)

    def __iadd__(self, other):
        self.write(other)
        return self
