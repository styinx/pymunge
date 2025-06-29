from pathlib import Path

from app.environment import MungeEnvironment as ENV
from swbf.builders.builder import UcfbNode, int32_data, string_data, float32_array_data
from swbf.builders.builder import StringProperty, BinaryProperty
from swbf.builders.builder import Magic, SwbfUcfbBuilder
from swbf.parsers.msh import MshParser, MshChunk
from swbf.parsers.msh import Header, Mesh, SceneInformation, Model, ModelType, Name, FlagsModel, ParentModel, TransformModel
from util.diagnostic import ErrorMessage


class ModelBuilderError(ErrorMessage):
    TOPIC = 'MSH'


class MissingMshChunk(ModelBuilderError):
    def __init__(self, node: type[MshChunk], filepath: Path):
        super().__init__(f'Missing MSH Chunk "{node.TYPE}" in file {filepath}')


class ModelChunk:
    INFO = 'INFO'
    NAME = 'NAME'
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
    extension = 'model'

    def __init__(self, tree: MshParser):
        SwbfUcfbBuilder.__init__(self, tree, Magic.Skeleton)

    def build(self):
        mesh = self.tree.find_nested(Mesh)

        if not mesh:
            ENV.Diag.report(MissingMshChunk(Mesh, self.tree.filepath))

        for scene_information in mesh.find_all(SceneInformation):
            pass

        model_names = {}
        model_parents = []
        model_transforms = bytearray()

        for model in mesh.find_all(Model):
            model_name = model.find(Name)
            model_type = model.find(ModelType)
            model_parent = model.find(ParentModel)
            model_transform = model.find(TransformModel)

            if not model_name:
                ENV.Diag.report(MissingMshChunk(Name, self.tree.filepath))
            if not model_type:
                ENV.Diag.report(MissingMshChunk(ModelType, self.tree.filepath))

            if model_name and model_type:
                if not model_name.name.startswith('p_') \
                    and model_name.name.find('_lowrez') == -1 \
                    and model_type.model_type != ModelType.ShadowVolume:

                    model_names[model_name.name.rstrip('\0')] = model

                    if model_parent:
                        model_parents.append(model_parent.name.rstrip('\0'))
                    else:
                        model_parents.append('')

                    if model_transform:
                        print(model_name.name)
                        print(model_transform.dump(properties=True))
                        import glm

                        # Quaternion: x, y, z, w
                        q = glm.quat(*[0.0 if x == -0.0 else x for x in model_transform.rotation])  # glm uses w-first order

                        # Get 3x3 matrix
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

        return self
