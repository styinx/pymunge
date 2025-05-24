from swbf.builders.builder import int32_data
from swbf.builders.builder import StringProperty, BinaryProperty
from swbf.builders.builder import Magic, SwbfUcfbBuilder
from swbf.builders.fnv1a import fnv1a_32
from swbf.parsers.odf import OdfParser, Section, Key, Reference, Value


class Class(SwbfUcfbBuilder):

    def __init__(self, tree: OdfParser):
        SwbfUcfbBuilder.__init__(self, tree, Magic.Entc)

    def build(self):
        try:
            it = self.tree.walk()
            while it:
                node = next(it)
                if isinstance(node, Key):
                    if node.name == OdfParser.Key.ClassLabel:
                        class_label = next(it)

                        if not isinstance(class_label, Value):
                            raise Exception('TODO')

                        base_property = StringProperty('BASE', class_label.value.replace('"', ''))
                        self.add(base_property)

                        name_property = StringProperty('TYPE', self.tree.filepath.stem)  # odf name
                        self.add(name_property)

                    else:
                        # TODO: filter out duplicates and invalid props

                        val = next(it)
                        if isinstance(val, Reference):
                            prop = BinaryProperty(
                                'PROP',
                                int32_data(fnv1a_32(node.name)) + (val.filepath.stem.replace('"', '') + chr(0)).encode('utf-8')
                            )
                            self.add(prop)
                        elif isinstance(val, Value):
                            prop = BinaryProperty(
                                'PROP',
                                int32_data(fnv1a_32(node.name)) + (val.value.replace('"', '') + chr(0)).encode('utf-8')
                            )
                            self.add(prop)
                        else:
                            raise Exception('TODO')

        except StopIteration:
            pass

        return self
