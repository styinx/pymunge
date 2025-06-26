from pathlib import Path
import sys
from logging import Logger

from parxel.nodes import Node, BinaryNode
from parxel.parser import BinaryParser

from swbf.parsers.parser import SwbfBinaryParser
from util.logging import get_logger


class MshChunk:
    type = ''

    # Level 0
    HEDR = 'HEDR'

    # Level 1
    ANM2 = 'ANM2'
    BLN2 = 'BLN2'
    CL1L = 'CL1L'
    MSH2 = 'MSH2'
    SHVO = 'SHVO'
    SKL2 = 'SKL2'

    # Level 2
    CAMR = 'CAMR'
    CYCL = 'CYCL'
    KFR3 = 'KFR3'
    MATL = 'MATL'
    MODL = 'MODL'
    SINF = 'SINF'

    # Level 3
    GEOM = 'GEOM'
    MATD = 'MATD'
    SWCI = 'SWCI'

    # Level 4
    CLTH = 'CLTH'
    SEGM = 'SEGM'

    # Level 5
    STRP = 'STRP'

    # Leaves
    ATRB = 'ATRB'
    BBOX = 'BBOX'
    BPRS = 'BPRS'
    CLRB = 'CLRB'
    CLRL = 'CLRL'
    CMSH = 'CMSH'
    COLL = 'COLL'
    CPOS = 'CPOS'
    CPRS = 'CPRS'
    CTEX = 'CTEX'
    CUV0 = 'CUV0'
    DATA = 'DATA'
    ENVL = 'ENVL'
    FIDX = 'FIDX'
    FLGS = 'FLGS'
    FRAM = 'FRAM'
    FWGT = 'FWGT'
    NAME = 'NAME'
    NDXL = 'NDXL'
    NDXT = 'NDXT'
    NRML = 'NRML'
    MATI = 'MATI'
    MNDX = 'MNDX'
    MTYP = 'MTYP'
    POSL = 'POSL'
    PRNT = 'PRNT'
    SHDW = 'SHDW'
    SPRS = 'SPRS'
    TRAN = 'TRAN'
    TX0D = 'TX0D'
    UV0L = 'UV0L'
    WGHT = 'WGHT'

    def __init__(self, msh_stream: BinaryParser):
        self.chunk_name : str = msh_stream.string(4)
        self.chunk_length : int = msh_stream.int32()


class Header(MshChunk, BinaryNode):
    type = MshChunk.HEDR

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


# Level 1


class Animation(MshChunk, BinaryNode):
    type = MshChunk.ANM2

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class BlendFactor(MshChunk, BinaryNode):
    type = MshChunk.BLN2

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ClosingChunk(MshChunk, BinaryNode):
    type = MshChunk.CL1L

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Mesh(MshChunk, BinaryNode):
    type = MshChunk.MSH2

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ShadowVolume(MshChunk, BinaryNode):
    type = MshChunk.SHVO

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.has_shadow_volume = bool(msh_stream.int32())

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Skeleton(MshChunk, BinaryNode):
    type = MshChunk.SKL2

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


# Level 2


class AnimationCycle(MshChunk, BinaryNode):
    type = MshChunk.CYCL

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_animations: int = msh_stream.int32()

        self.animations = []
        for _ in range(self.num_animations):
            animation_name: str = msh_stream.string(64)
            fps: float = msh_stream.float32()
            first_frame: float = msh_stream.float32()
            last_frame: float = msh_stream.float32()
            self.animations.append((animation_name, fps, first_frame, last_frame))

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Camera(MshChunk, BinaryNode):
    type = MshChunk.CAMR

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Keyframes(MshChunk, BinaryNode):
    type = MshChunk.KFR3

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_bones: int = msh_stream.int32()

        self.keyframes = []
        for _ in range(self.num_bones):
            crc: int = msh_stream.int32()
            keyframe_type: int = msh_stream.int32()
            num_translation_frames: int = msh_stream.int32()
            num_rotation_frames: int = msh_stream.int32()
            translation_frame_index: int = msh_stream.int32()
            translation: list[float] = msh_stream.float32_array(3)
            rotation_frame_index: int = msh_stream.int32()
            rotation: list[float] = msh_stream.float32_array(4)
            self.keyframes.append((
                crc,
                keyframe_type,
                num_translation_frames,
                num_rotation_frames,
                translation_frame_index,
                translation,
                rotation_frame_index,
                rotation
            ))

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Material(MshChunk, BinaryNode):
    type = MshChunk.MATL

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.materials : int = msh_stream.int32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Model(MshChunk, BinaryNode):
    type = MshChunk.MODL

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class SceneInformation(MshChunk, BinaryNode):
    type = MshChunk.SINF

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


# Level 3


class MaterialData(MshChunk, BinaryNode):
    type = MshChunk.MATD

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Geometry(MshChunk, BinaryNode):
    type = MshChunk.GEOM

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


# Level 4


class ClothHeader(MshChunk, BinaryNode):
    type = MshChunk.CLTH

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class SegmentHeader(MshChunk, BinaryNode):
    type = MshChunk.SEGM

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Strip(MshChunk, BinaryNode):
    type = MshChunk.STRP

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_indices: int = msh_stream.int32()
        self.polygons: list[int] = [msh_stream.int16() for _ in range(self.num_indices)]

        # Skip potential padding (2 * 16 bits per entry for 32 bit alignment)
        msh_stream.advance((self.num_indices * 2) % 4)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


# Leaves


class Attributes(MshChunk, BinaryNode):
    type = MshChunk.ATRB

    Emissive = 1
    Glow = 2
    SingleTransparency = 4
    DoubleTransparency = 8
    HardEdgeTransparency = 16
    PerPixelLightning = 32
    AdditiveTransparency = 64
    Specular = 128

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.sum: int = msh_stream.advance(1)[0]
        self.render_type: int = msh_stream.advance(1)[0]
        self.data0: int = msh_stream.advance(1)[0]
        self.data1: int = msh_stream.advance(1)[0]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class BendConstraints(MshChunk, BinaryNode):
    type = MshChunk.BPRS

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_constraints: int = msh_stream.int32()
        self.constraints: list[list[int]]= [msh_stream.int16_array(2) for _ in range(self.num_constraints)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class BoundingBox(MshChunk, BinaryNode):
    type = MshChunk.BBOX

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.rotation: list[float] = msh_stream.float32_array(4)
        self.center: list[float] = msh_stream.float32_array(3)
        self.extension: list[float] = msh_stream.float32_array(3)
        self.radius: float = msh_stream.float32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ClothMesh(MshChunk, BinaryNode):
    type = MshChunk.CMSH

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        # TODO: is it 3 or 4 elements?
        self.num_points: int = msh_stream.int32()
        self.constraints: list[list[float]]= [msh_stream.float32_array(3) for _ in range(self.num_points)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ClothTextureName(MshChunk, BinaryNode):
    type = MshChunk.CTEX

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.name: str = msh_stream.string(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ClothUvCoordinates(MshChunk, BinaryNode):
    type = MshChunk.CUV0

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_coordinates: int = msh_stream.int32()
        self.coordinates: list[list[float]]= [msh_stream.float32_array(2) for _ in range(self.num_coordinates)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ClothVertecies(MshChunk, BinaryNode):
    type = MshChunk.CPOS

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_vertecies: int = msh_stream.int32()
        self.constraints: list[list[float]]= [msh_stream.float32_array(3) for _ in range(self.num_vertecies)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Collision(MshChunk, BinaryNode):
    type = MshChunk.COLL

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        #TODO: name lengths, 64 for now

        self.num_collisions: int = msh_stream.int32()
        self.collision_name: str = msh_stream.string(64)
        self.parent_name: str = msh_stream.string(64)
        self.primitive_type: int = msh_stream.int32()
        self.data0: float = msh_stream.float32()
        self.data1: float = msh_stream.float32()
        self.data2: float = msh_stream.float32()

        # Padding
        msh_stream.advance(msh_stream.pos % 4)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class CollisionPrimitive(MshChunk, BinaryNode):
    type = MshChunk.SWCI

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.primitive_type: int = msh_stream.int32()
        self.data0: float = msh_stream.float32()
        self.data1: float = msh_stream.float32()
        self.data2: float = msh_stream.float32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ColorVertex(MshChunk, BinaryNode):
    type = MshChunk.CLRB

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.colors: bytes = msh_stream.bytes(4)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ColorVertecies(MshChunk, BinaryNode):
    type = MshChunk.CLRL

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_colors: int = msh_stream.int32()
        self.colors: list[bytes] = [msh_stream.bytes(4) for _ in range(self.num_colors)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class CrossConstraints(MshChunk, BinaryNode):
    type = MshChunk.CPRS

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_coordinates: int = msh_stream.int32()
        self.coordinates: list[list[float]]= [msh_stream.float32_array(3) for _ in range(self.num_coordinates)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class DataCamera(MshChunk, BinaryNode):
    type = MshChunk.DATA

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        # TODO
        self._todo : bytes = msh_stream.advance(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class DataMaterial(MshChunk, BinaryNode):
    type = MshChunk.DATA

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.diffuse_color : list[float] = msh_stream.float32_array(4)
        self.specular_color : list[float] = msh_stream.float32_array(4)
        self.ambient_color : list[float] = msh_stream.float32_array(4)
        self.specular_sharpness : float = msh_stream.float32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Envelope(MshChunk, BinaryNode):
    type = MshChunk.ENVL

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_indices : int = msh_stream.int32()
        self.indices : list[int] = msh_stream.int32_array(self.num_indices)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class FixPoints(MshChunk, BinaryNode):
    type = MshChunk.FIDX

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_points : int = msh_stream.int32()
        self.indices : list[int] = msh_stream.int32_array(self.num_indices)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class FixPointWeights(MshChunk, BinaryNode):
    type = MshChunk.FWGT

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        # TODO: string size

        self.num_points : int = msh_stream.int32()
        self.weights : list[str] = [msh_stream.string(64) for _ in range(self.num_points)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class FlagsModel(MshChunk, BinaryNode):
    type = MshChunk.FLGS

    Hidden = 1
    DynamicallyLit = 2
    RetainNormals = 4
    RenderAfterShadows = 8
    DontFlattenGeometry = 16
    PS2Optimize = 32

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.flags : int = msh_stream.int32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Frame(MshChunk, BinaryNode):
    type = MshChunk.FRAM

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.frame_start: int = msh_stream.int32()
        self.frame_end: int = msh_stream.int32()
        self.fps: float = msh_stream.float32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Name(MshChunk, BinaryNode):
    type = MshChunk.NAME

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.name: str = msh_stream.string(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Normals(MshChunk, BinaryNode):
    type = MshChunk.NRML

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_normals: int = msh_stream.int32()
        self.normals: list[list[float]] = [msh_stream.float32_array(3) for _ in range(self.num_normals)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class MaterialIndex(MshChunk, BinaryNode):
    type = MshChunk.MATI

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.material_index : int = msh_stream.int32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ModelIndex(MshChunk, BinaryNode):
    type = MshChunk.MNDX

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.model_index : int = msh_stream.int32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ModelType(MshChunk, BinaryNode):
    type = MshChunk.MTYP

    Null = 0
    Dynamic = 1
    Cloth = 2
    Bone = 3
    Static = 4
    ShadowVolume = 6
    Destructable = 7

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.model_type : int = msh_stream.int32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ParentModel(MshChunk, BinaryNode):
    type = MshChunk.PRNT

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.name : str = msh_stream.string(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Polygons(MshChunk, BinaryNode):
    type = MshChunk.NDXL

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        # TODO
        self.todo = msh_stream.bytes(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class PositionVertices(MshChunk, BinaryNode):
    type = MshChunk.POSL

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_positions : int = msh_stream.int32()
        self.positions : list[list[float]] = [msh_stream.float32_array(3) for _ in range(self.num_positions)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ShadowMesh(MshChunk, BinaryNode):
    type = MshChunk.SHDW

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_vertices: int = msh_stream.int32()
        self.vertices: list[list[float]] = [msh_stream.float32_array(3) for _ in range(self.num_vertices)]
        self.num_edges: int = msh_stream.int32()
        self.edges: list[list[int]] = [msh_stream.int16_array(4) for _ in range(self.num_vertices)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class StretchConstraints(MshChunk, BinaryNode):
    type = MshChunk.SPRS

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_constraints: int = msh_stream.int32()
        self.constraints: list[list[int]] = [msh_stream.int16_array(2) for _ in range(self.num_constraints)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Texture(MshChunk, BinaryNode):
    type = MshChunk.TX0D

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.name: str = msh_stream.string(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class TransformModel(MshChunk, BinaryNode):
    type = MshChunk.TRAN

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.scale : list[float] = msh_stream.float32_array(3)
        self.rotation : list[float] = msh_stream.float32_array(4)
        self.translation : list[float] = msh_stream.float32_array(3)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Triangles(MshChunk, BinaryNode):
    type = MshChunk.NDXT

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        # TODO
        self.todo = msh_stream.bytes(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class UvCoordinates(MshChunk, BinaryNode):
    type = MshChunk.UV0L

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_coordinates : int = msh_stream.int32()
        self.coordinates : list[list[float]] = [msh_stream.float32_array(2) for _ in range(self.num_coordinates)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class WeightBones(MshChunk, BinaryNode):
    type = MshChunk.WGHT

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        MshChunk.__init__(self, msh_stream)

        self.num_weights : int = msh_stream.int32()
        self.weights : list[tuple[int, float]] = [(msh_stream.int32(), msh_stream.float32()) for _ in range(self.num_weights)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class MshParser(SwbfBinaryParser):
    extension = 'msh'

    def __init__(self, filepath: Path, buffer: bytes = None, logger : Logger = get_logger(__name__)):
        SwbfBinaryParser.__init__(self, filepath=filepath, buffer=buffer, logger=logger)

    def _parse_chunk(self, children: dict) -> BinaryNode | Node | None:
        child_name = self.string(4)
        child_len = self.int32()
        self.pos -= 8

        parse_children, child_type = children.get(child_name, (None, None))

        # The chunk is a valid child
        if child_type:
            node = child_type(self)
            self.scope.add(node)
        else:
            if hasattr(self.scope, 'parent') and self.scope.parent:
                self.scope = self.scope.parent
            return None

        # The chunk has children
        if parse_children:
            self.scope = node
            parse_children()
            return self.scope

        # The chunk is a leaf
        else:
            return self.scope

    def parse_format(self):
        self._parse_chunk({
            MshChunk.HEDR: (self.parse_hedr, Header)
        })

        return self

    # Level 0

    def parse_hedr(self):
        while self._parse_chunk({
            MshChunk.ANM2: (self.parse_anm2, Animation),
            MshChunk.BLN2: (None, BlendFactor),
            MshChunk.CL1L: (None, ClosingChunk),
            MshChunk.MSH2: (self.parse_msh2, Mesh),
            MshChunk.SKL2: (None, Skeleton),
            MshChunk.SHVO: (None, ShadowVolume),
        }):
            pass

    # Level 1

    def parse_anm2(self):
        while self._parse_chunk({
            MshChunk.CYCL: (self.parse_camr, AnimationCycle),
            MshChunk.KFR3: (self.parse_matl, Keyframes),
        }):
            pass

    def parse_msh2(self):
        while self._parse_chunk({
            MshChunk.CAMR: (self.parse_camr, Camera),
            MshChunk.MATL: (self.parse_matl, Material),
            MshChunk.MODL: (self.parse_modl, Model),
            MshChunk.SINF: (self.parse_sinf, SceneInformation),
        }):
            pass

    def parse_shv0(self):
        pass

    def parse_skl2(self):
        pass

    # Level 2

    def parse_camr(self):
        while self._parse_chunk({
            MshChunk.DATA: (None, DataCamera),
            MshChunk.NAME: (None, Name),
        }):
            pass

    def parse_matl(self):
        while self._parse_chunk({
            MshChunk.MATD: (self.parse_matd, MaterialData),
        }):
            pass

    def parse_modl(self):
        while self._parse_chunk({
            MshChunk.FLGS: (None, FlagsModel),
            MshChunk.GEOM: (self.parse_geom, Geometry),
            MshChunk.NAME: (None, Name),
            MshChunk.MNDX: (None, ModelIndex),
            MshChunk.MTYP: (None, ModelType),
            MshChunk.PRNT: (None, ParentModel),
            MshChunk.SWCI: (None, CollisionPrimitive),
            MshChunk.TRAN: (None, TransformModel)
        }):
            pass

    def parse_sinf(self):
        while self._parse_chunk({
            MshChunk.BBOX: (None, BoundingBox),
            MshChunk.FRAM: (None, Frame),
            MshChunk.NAME: (None, Name)
        }):
            pass

    # Level 3

    def parse_geom(self):
        while self._parse_chunk({
            MshChunk.BBOX: (None, BoundingBox),
            MshChunk.CLTH: (self.parse_clth, ClothHeader),
            MshChunk.ENVL: (None, Envelope),
            MshChunk.SEGM: (self.parse_segm, SegmentHeader)
        }):
            pass

    def parse_matd(self):
        while self._parse_chunk({
            MshChunk.ATRB: (None, Attributes),
            MshChunk.NAME: (None, Name),
            MshChunk.DATA: (None, DataMaterial),
            MshChunk.TX0D: (None, Texture)
        }):
            pass

    # Level 4

    def parse_segm(self):
        while self._parse_chunk({
            MshChunk.CLRB: (None, ColorVertex),
            MshChunk.CLRL: (None, ColorVertecies),
            MshChunk.MATI: (None, MaterialIndex),
            MshChunk.NDXL: (None, Polygons),
            MshChunk.NDXT: (None, Triangles),
            MshChunk.NRML: (None, Normals),
            MshChunk.POSL: (None, PositionVertices),
            MshChunk.SHDW: (None, ShadowMesh),
            MshChunk.STRP: (self.parse_strp, Strip),
            MshChunk.UV0L: (None, UvCoordinates),
            MshChunk.WGHT: (None, WeightBones)
        }):
            pass

    def parse_clth(self):
        while self._parse_chunk({
            # TODO
            MshChunk.BPRS: (None, BendConstraints),
            MshChunk.CMSH: (None, ClothMesh),
            MshChunk.COLL: (None, Collision),
            MshChunk.CPOS: (None, ClothVertecies),
            MshChunk.CPRS: (None, CrossConstraints),
            MshChunk.CTEX: (None, ClothTextureName),
            MshChunk.CUV0: (None, ClothUvCoordinates),
            MshChunk.FIDX: (None, FixPoints),
            MshChunk.FWGT: (None, FixPointWeights),
            MshChunk.SPRS: (None, StretchConstraints)
        }):
            pass

    # Level 5

    def parse_strp(self):
        while self._parse_chunk({
            MshChunk.BBOX: (None, BoundingBox),
            MshChunk.FRAM: (None, Frame),
            MshChunk.NAME: (None, Name)
        }):
            pass


if __name__ == '__main__':
    MshParser.cmd_helper()

    # TODO: Global exit code
    sys.exit(0)
