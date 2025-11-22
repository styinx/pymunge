from pathlib import Path

from pyglm import glm

from app.environment import MungeEnvironment as ENV
from swbf.builders.builder import Ext
from swbf.builders.builder import UcfbNode, int32_data, string_data, float32_array_data
from swbf.builders.builder import StringProperty, BinaryProperty
from swbf.builders.builder import Magic, SwbfUcfbBuilder
from swbf.parsers.msh import MshParser, MshChunk
from swbf.parsers.msh import Header, Mesh, SceneInformation, Name
from swbf.parsers.msh import Model, ModelType, ModelIndex, FlagsModel, ParentModel, TransformModel
from util.diagnostic import ErrorMessage


class ModelBuilderError(ErrorMessage):
    TOPIC = 'MSH'


class MissingMshChunk(ModelBuilderError):
    def __init__(self, node: type[MshChunk], filepath: Path):
        super().__init__(f'Missing MSH Chunk "{node.TYPE}" in file {filepath}')


class ModelChunk:
    INFO = 'INFO'
    NAME = 'NAME'
    NODE = 'NODE'
    PRNT = 'PRNT'
    XFRM = 'XFRM'


class ModelInfoProperty(UcfbNode):
    def __init__(self, magic: str, name: str, models: int, pad: bool = True):
        UcfbNode.__init__(self)

        self.magic: str = magic
        self.name: str = name
        self.models: int = models
        self.pad: str = ''

        self.name += '\0'

        if pad:
            alignment = len(self.name) % 4
            if alignment != 0:
                self.pad += '\0' * (4 - alignment)

        self.length: int = len(name) + 1 + 4 + len(self.pad)

    def __len__(self) -> int:
        # MAGIC , SIZE , (name , number)
        return 4 + 4 + self.length

    def data(self) -> bytes:
        return string_data(self.magic) + int32_data(self.length + 4) + string_data(self.name) + int32_data(self.models) + string_data(self.pad)


class ModelBuilder(SwbfUcfbBuilder):
    Extension = Ext.Model

    def __init__(self, tree: MshParser):
        SwbfUcfbBuilder.__init__(self, tree, Magic.Skeleton)

    def build(self):
        mesh = self.tree.find_nested(Mesh)

        if not mesh:
            ENV.Diag.report(MissingMshChunk(Mesh, self.tree.filepath))
            return self

        for scene_information in mesh.find_all(SceneInformation):
            pass

        model_root = None
        model_names = {}
        model_parents = []
        model_transforms = bytearray()

        model_order = {}

        for model in mesh.find_all(Model):
            if model_root is None:
                model_root = model

            model_name = model.find(Name)
            model_type = model.find(ModelType)
            model_parent = model.find(ParentModel)
            model_transform = model.find(TransformModel)

            if not model_name:
                ENV.Diag.report(MissingMshChunk(Name, self.tree.filepath))
            if not model_type:
                ENV.Diag.report(MissingMshChunk(ModelType, self.tree.filepath))

            if not model_name and not model_type:
                continue

            if model_type.model_type in [ModelType.Bone, ModelType.Static]:

                if model_name.name.startswith('p_') or model_name.name.endswith('_lowrez'):
                    continue

                model_names[model_name.name.rstrip('\0')] = model

                print(model_name.name)
                #print(model_type.dump(recursive=False, properties=True))

                if model_parent:
                    if model_parent.name.rstrip('\0') in model_order:
                        model_order[model_parent.name.rstrip('\0')] = model_name.name.rstrip('\0')
                        model_parents.append(model_parent.name.rstrip('\0'))
                else:
                    model_parents.append('')
                    model_order[model_name.name.rstrip('\0')] = {}

                if model_transform:
                    q = glm.quat(*[0.0 if x == -0.0 else x for x in model_transform.rotation])

                    rotation_matrix = glm.mat3_cast(q)
                    model_transforms += rotation_matrix.to_bytes()
                    model_transforms += float32_array_data(model_transform.translation)

        info_property = ModelInfoProperty(ModelChunk.INFO, self.tree.filepath.stem, len(model_names))
        self.add(info_property)

        model_names = '\0'.join(model_names.keys())
        name_property = StringProperty(ModelChunk.NAME, model_names)
        self.add(name_property)

        model_parents = '\0'.join(model_parents)
        parent_property = StringProperty(ModelChunk.PRNT, model_parents)
        self.add(parent_property)

        model_transforms = model_transforms
        transform_property = BinaryProperty(ModelChunk.XFRM, model_transforms)
        self.add(transform_property)

        modl = SwbfUcfbBuilder(self.tree, Magic.Model)

        modl_name_property = StringProperty(ModelChunk.NAME, self.tree.filepath.stem)
        modl.add(modl_name_property)

        modl_node = model_root.find(Name)
        modl_node_property = StringProperty(ModelChunk.NODE, modl_node.name)
        modl.add(modl_node_property)

        self.add(modl)

        return self
