from swbf.builders.ucfb import int32_data
from swbf.builders.ucfb import StringProperty, BinaryProperty
from swbf.builders.ucfb import Magic, Chunk
from swbf.builders.fnv1a import fnv1a_32
from swbf.parsers.odf import Odf, Section, Key, Reference, Value


class Class(Chunk):
    def __init__(self, tree: Odf):
        Chunk.__init__(self, Magic.Entc)

        self.tree = tree

    def build(self):
        try:
            it = self.tree.walk()
            while it:
                node = next(it)
                if isinstance(node, Key):
                    if node.name == Odf.Key.ClassLabel:
                        class_label = next(it)

                        if not isinstance(class_label, Value):
                            raise Exception('TODO')

                        base_property = StringProperty('BASE', class_label.value.replace('"', ''))
                        self.add(base_property)

                        name_property = StringProperty('TYPE', self.tree.filepath.stem) # odf name
                        self.add(name_property)

                    else:
                        # TODO: filter out duplicates and invalid props

                        val = next(it)
                        if isinstance(val, Reference):
                            prop = BinaryProperty('PROP', int32_data(fnv1a_32(node.name)) + val.filepath.stem.replace('"', '').encode('utf-8'))
                            self.add(prop)
                        elif isinstance(val, Value):
                            prop = BinaryProperty('PROP', int32_data(fnv1a_32(node.name)) + val.value.replace('"', '').encode('utf-8'))
                            self.add(prop)
                        else:
                            raise Exception('TODO')

        except StopIteration:
            pass

        return self

