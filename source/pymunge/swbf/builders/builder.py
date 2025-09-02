import struct

from parxel.nodes import Document

from util.enum import Enum
from swbf.parsers.req import ReqParser


class Ext(Enum):
    Class = 'class'
    Model = 'model'


class Magic(Enum):
    Arcs = 'ARCS'
    Barrier = 'BARR'
    Base = 'BASE'
    Bin_ = 'BIN_'
    Bnam = 'BNAM'
    Data = 'DATA'
    Dxt1 = 'DXT1'
    Dxt3 = 'DXT3'
    EntityClass = 'entc'
    ExplosionClass = 'expc'
    Face = 'FACE'
    Flag = 'FLAG'
    Format = 'FMT_'
    Gmod = 'gmod'
    Ibuf = 'IBUF'
    Info = 'INFO'
    Leaf = 'LEAF'
    Level = 'lvl_'
    Localization = 'Locl'
    Lod0 = 'LOD0'
    Name = 'NAME'
    Node = 'NODE'
    Material = 'MTRL'
    Mina = 'MINA'
    Model = 'modl'
    OrdnanceClass = 'ordc'
    Plan = 'plan'
    Property = 'PROP'
    Prnt = 'PRNT'
    Region = 'regn'
    Rtyp = 'RTYP'
    Script = 'scr_'
    Scop = 'SCOP'
    Segm = 'segm'
    Size = 'SIZE'
    Sky = 'sky_'
    Skeleton = 'skel'
    Snam = 'SNAM'
    Sphr = 'SPHR'
    Texture = 'tex_'
    Tada = 'TADA'
    TextureName = 'TNAM'
    Tnja = 'TNJA'
    Tree = 'TREE'
    Type = 'TYPE'
    Ucfb = 'ucfb'
    Vbuf = 'VBUF'
    WeaponClass = 'wpnc'
    Xfrm = 'XFRM'


def string_data(string: str) -> bytes:
    return string.encode('utf-8')


def int32_data(number: int) -> bytes:
    return number.to_bytes(length=4, byteorder='little')


def float32_data(number: float) -> bytes:
    return struct.pack('<f', number)


def float32_array_data(numbers: list[float]) -> bytes:
    return struct.pack(f'<{len(numbers)}f', *numbers)


class UcfbNode:

    def __init__(self):
        self.parent = None
        self.children: list = []

    def add(self, node):
        node.parent = self
        self.children.append(node)


class StringProperty(UcfbNode):

    def __init__(self, magic: str, string: str, pad: bool = True):
        UcfbNode.__init__(self)

        self.magic: str = magic
        self.string: str = string.rstrip('\0') + '\0'
        self.string_length: int = len(self.string)
        self.padding: str = ''
        self.padding_length: int = 0

        if pad:
            alignment = self.string_length % 4
            if alignment != 0:
                self.padding += '\0' * (4 - alignment)
                self.padding_length = len(self.padding)

    def __len__(self) -> int:
        # MAGIC , SIZE , string , padding
        return 4 + 4 + self.string_length + self.padding_length

    def data(self) -> bytes:
        return string_data(self.magic) + int32_data(self.string_length) + string_data(self.string + self.padding)


class NumberProperty(UcfbNode):

    def __init__(self, magic: str, number: int):
        UcfbNode.__init__(self)

        self.magic: str = magic
        self.number: int = number

    def __len__(self) -> int:
        # MAGIC , number
        return 4 + 4

    def data(self) -> bytes:
        return string_data(self.magic) + int32_data(self.number)


class BinaryProperty(UcfbNode):

    def __init__(self, magic: str, buffer: bytearray, pad: bool = True):
        UcfbNode.__init__(self)

        self.magic: str = magic
        self.buffer: bytearray = buffer
        self.buffer_length: int = len(buffer)
        self.padding: bytearray = bytearray()
        self.padding_length: int = 0

        if pad:
            alignment = self.buffer_length % 4
            if alignment != 0:
                self.padding += bytes([0] * (4 - alignment))
                self.padding_length = len(self.padding)

    def __len__(self) -> int:
        # MAGIC , SIZE , buffer , padding
        return 4 + 4 + self.buffer_length + self.padding_length

    def data(self) -> bytes:
        return string_data(self.magic) + int32_data(self.buffer_length) + self.buffer + self.padding


class SwbfUcfbBuilder(UcfbNode):
    Extension = 'bin' # TODO

    def __init__(self, tree: Document, magic: str):
        UcfbNode.__init__(self)

        self.tree: Document = tree
        self.magic: str = magic
        self.buffer: bytearray = bytearray()

    def __len__(self) -> int:
        # MAGIC , SIZE , children with padded length
        return 4 + 4 + sum(map(lambda x: len(x.data()), self.children))

    def build(self):
        raise NotImplementedError(
            f'This is an abstract base class! '
            f'Implement "build(self)" for class "{self.__class__.__name__}"'
        )

    def data(self) -> bytearray:
        buffer = bytearray()
        buffer += string_data(self.magic)
        buffer += int32_data(len(self) - 4 - 4)  # no MAGIC and SIZE

        for child in self.children:
            buffer += child.data()

        padding = len(self.buffer) % 4
        if padding != 0:
            buffer += string_data('\0' * (4 - padding))

        return buffer

    def dump(self, width: int = 16):
        dump: str = ''
        buffer = self.data()

        dump += ' ' * 8
        for idx in range(width):
            dump += f' {idx:02X}'
        dump += '\n'

        row: int = 0
        pos: int = 0
        while pos < len(buffer):

            line = buffer[pos:pos + width]
            buf_len = len(line)

            dump += f'{row:08X}'
            for idx in range(buf_len):
                dump += f' {line[idx]:02X}'

            if buf_len < width:
                for idx in range(width - buf_len):
                    dump += f'   '

            dump += '  '
            for idx in range(buf_len):
                sym = line[idx]

                # Decode only ASCII
                if 0x20 <= sym <= 0x7E:
                    dump += chr(sym)
                else:
                    dump += '.'

            dump += '\n'
            pos += width
            row += 1

        return dump


class Ucfb(SwbfUcfbBuilder):
    "Universal Chunk Format Block (UCFB)"

    def __init__(self, tree: ReqParser):
        SwbfUcfbBuilder.__init__(self, tree, Magic.Ucfb)

    def build(self):
        return self


class Script(SwbfUcfbBuilder):

    def __init__(self, name: str, info: str, body: bytearray):
        SwbfUcfbBuilder.__init__(self, Magic.Script)

        name_property = StringProperty('NAME', name)
        info_property = StringProperty('INFO', info)
        body_property = BinaryProperty('BODY', body)

        self.add(name_property)
        self.add(info_property)
        self.add(body_property)


class Skeleton(SwbfUcfbBuilder):

    def __init__(self, name: str, root: str, properties: dict):
        SwbfUcfbBuilder.__init__(self, Magic.Skeleton)

        info_property = StringProperty('INFO', name)  # msh name
        name_property = StringProperty('NAME', root)  # root name

        self.add(info_property)
        self.add(name_property)


if __name__ == '__main__':
    pass
