from pathlib import Path
import sys
from logging import Logger

from parxel.nodes import Node, BinaryNode
from parxel.token import TK, Token

from app.registry import FileRegistry, Dependency
from swbf.parsers.format import BinaryFormat
from util.logging import get_logger
from util.enum import Enum


logger = get_logger(__name__)


class Frame(BinaryNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        BinaryNode.__init__(self, buffer, parent)

        self.frame_start: int = int.from_bytes(buffer[0:4])
        self.frame_end: int = int.from_bytes(buffer[4:8])
        self.frames_per_second: int = int.from_bytes(buffer[4:8])


class Msh(BinaryFormat):

    class Chunk:
        # Level 0
        HEDR = 'HEDR'

        # Level 1
        ANM2 = 'ANM2'
        BLN2 = 'BLN2'
        CL1L = 'CL1L'
        MSH2 = 'MSH2'
        SHV0 = 'SHV0'
        SKL2 = 'SKL2'

        # Level 2
        BBOX = 'BBOX'
        CAMR = 'CAMR'
        CYCL = 'CYCL'
        FRAM = 'FRAM'
        KFR3 = 'KFR3'
        NAME = 'NAME'
        MATL = 'MATL'
        MODL = 'MODL'
        SINF = 'SINF'

    def __init__(self, registry: FileRegistry, filepath: Path, buffer: bytes = None, logger : Logger = logger):
        BinaryFormat.__init__(self, registry=registry, filepath=filepath, buffer=buffer, logger=logger)

    def _parse_chunk(self, children: dict):
        child_name = self.string(4)
        child_len = self.int32()

        print(child_name)

        parse_child, child_type, is_primitive = children.get(child_name, (None, None, None))
        if parse_child:
            if is_primitive:
                self.advance(child_len)
                child_type(self.collect_bytes(), self)
                return self # TODO return parent
            else:
                parse_child()
                node = child_type(self.collect_bytes(), self)
            return node

        else:
            self.logger.error(f'"{"\" | \"".join(children.keys())}" expected, got "{child_name}"')

        return BinaryNode(self.collect_bytes())

    def parse_format(self):
        self._parse_chunk({
            Msh.Chunk.HEDR: (self.parse_hedr, BinaryNode, False)
        })

        return self

    def parse_hedr(self):
        return self._parse_chunk({
            Msh.Chunk.ANM2: (self.parse_anm2, BinaryNode),
            Msh.Chunk.BLN2: (self.parse_bln2, BinaryNode),
            Msh.Chunk.CL1L: (self.parse_cl1l, BinaryNode),
            Msh.Chunk.MSH2: (self.parse_msh2, BinaryNode, False),
            Msh.Chunk.SHV0: (self.parse_shv0, BinaryNode),
            Msh.Chunk.SKL2: (self.parse_skl2, BinaryNode),
        })

    def parse_anm2(self):
        pass

    def parse_bln2(self):
        pass

    def parse_cl1l(self):
        pass

    def parse_msh2(self):
        return self._parse_chunk({
            Msh.Chunk.CAMR: (self.parse_camr, BinaryNode),
            Msh.Chunk.MATL: (self.parse_matl, BinaryNode),
            Msh.Chunk.MODL: (self.parse_modl, BinaryNode),
            Msh.Chunk.SINF: (self.parse_sinf, BinaryNode, False),
        })

    def parse_shv0(self):
        pass

    def parse_skl2(self):
        pass

    def parse_camr(self):
        pass

    def parse_matl(self):
        pass

    def parse_modl(self):
        pass

    def parse_sinf(self):
        return self._parse_chunk({
            Msh.Chunk.BBOX: (self.parse_bbox, BinaryNode),
            Msh.Chunk.FRAM: (self.parse_fram, Frame, True),
            Msh.Chunk.NAME: (self.parse_name, BinaryNode, True),
        })

    def parse_bbox(self):
        pass

    def parse_fram(self):
        return BinaryNode(bytes(0))

    def parse_name(self):
        return BinaryNode(bytes(0))


if __name__ == '__main__':
    Msh.cmd_helper()

    # TODO: Global exit code
    sys.exit(0)
