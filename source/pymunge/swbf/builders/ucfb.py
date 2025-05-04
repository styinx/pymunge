from util.enum import Enum


class Magic(Enum):
    Arcs = 'ARCS'
    Barrier = 'BARR'
    Base = 'BASE'
    Bin_ = 'BIN_'
    Bnam = 'BNAM'
    Data = 'DATA'
    Dxt1 = 'DXT1'
    Dxt3 = 'DXT3'
    Entc = 'entc'
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
    Xfrm = 'XFRM'


def string_data(string: str) -> bytes:
    return string.encode('utf-8')


def int32_data(number: int) -> bytes:
    return number.to_bytes(length=4, byteorder='little')


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
        self.string: str = string

        self.string += '\0'

        if pad:
            alignment = len(self.string) % 4
            if alignment != 0:
                self.string += '\0' * (4 - alignment)

    def __len__(self) -> int:
        # MAGIC , SIZE , string + (padding)
        return 4 + 4 + len(self.string)

    def data(self) -> bytes:
        return string_data(self.magic) + int32_data(len(self.string)) + string_data(self.string)


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

        if pad:
            alignment = len(self.buffer) % 4
            if alignment != 0:
                self.buffer += bytes([0] * (4 - alignment))

    def __len__(self) -> int:
        # MAGIC , SIZE , buffer
        return 4 + 4 + len(self.buffer)

    def data(self) -> bytes:
        return string_data(self.magic) + int32_data(len(self.buffer)) + self.buffer


class Chunk(UcfbNode):

    def __init__(self, magic: str):
        UcfbNode.__init__(self)

        self.magic: str = magic
        self.buffer: bytearray = bytearray()

    def __len__(self) -> int:
        # MAGIC , SIZE , children
        return 4 + 4 + sum(map(len, self.children))

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


class Ucfb(Chunk):
    "Universal Chunk Format Block (UCFB)"

    def __init__(self):
        Chunk.__init__(self, Magic.Ucfb)


class Script(Chunk):

    def __init__(self, name: str, info: str, body: bytearray):
        Chunk.__init__(self, Magic.Script)

        name_property = StringProperty('NAME', name)
        info_property = StringProperty('INFO', info)
        body_property = BinaryProperty('BODY', body)

        self.add(name_property)
        self.add(info_property)
        self.add(body_property)


class Skeleton(Chunk):

    def __init__(self, name: str, root: str, properties: dict):
        Chunk.__init__(self, Magic.Skeleton)

        info_property = StringProperty('INFO', name)  # msh name
        name_property = StringProperty('NAME', root)  # root name

        self.add(info_property)
        self.add(name_property)


class Model(Chunk):

    def __init__(self, name: str, root: str, properties: dict):
        Chunk.__init__(self, Magic.Model)

        name_property = StringProperty('NAME', name)  # msh name
        node_property = StringProperty('NODE', root)  # root name
        info_property = StringProperty('INFO', '?')

        self.add(name_property)
        self.add(node_property)
        self.add(info_property)


if __name__ == '__main__':
    ucfb = Ucfb()
    script = Script('bes2a', 'yummy', bytearray([1, 2, 3]))
    odf = Class('Light', 'rhnlightn', {'Color': '0 0 0 255', 'Size': '25'})
    msh = Model('platform', 'platform_root', {'Color': '0 0 0 255', 'Size': '25'})

    ucfb.add(script)
    ucfb.add(odf)
    ucfb.add(msh)

    ucfb.data()
    print(ucfb.dump())
