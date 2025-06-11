from swbf.builders.builder import int32_data
from swbf.builders.builder import StringProperty, BinaryProperty
from swbf.builders.builder import Magic, SwbfUcfbBuilder
from swbf.builders.fnv1a import fnv1a_32
from swbf.parsers.msh import *


class Model(SwbfUcfbBuilder):

    def __init__(self, tree: MshParser):
        SwbfUcfbBuilder.__init__(self, tree, Magic.Skeleton)

    def build(self):
        try:
            name_property = StringProperty('INFO', self.tree.filepath.stem, False)  # msh name
            self.add(name_property)

            it = self.tree.walk()
            while it:
                node = next(it)
                if isinstance(node, (Header, Mesh)):
                    pass  # skip

                elif isinstance(node, SceneInformation):
                    pass

        except StopIteration:
            pass

        return self
