from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.directives.patches import Figure


class ThemedFigureDirective(Figure):
    option_spec = Figure.option_spec.copy()
    option_spec['dark'] = directives.uri

    def run(self):
        node_list = super().run()
        dark_image_uri = self.options.get('dark')

        for node in node_list:
            if isinstance(node, nodes.figure) and dark_image_uri:
                for image_node in node.traverse(nodes.image):
                    light_uri = image_node['uri']
                    alt_text = image_node.get('alt', '')
                    light_html = f'<img src="{light_uri}" alt="{alt_text}" class="themed-figure light-img">'
                    dark_html = f'<img src="{dark_image_uri}" alt="{alt_text}" class="themed-figure dark-img">'
                    html = light_html + dark_html
                    raw_html = nodes.raw('', html, format='html')
                    image_node.replace_self(raw_html)
        return node_list


def setup(app):
    app.add_directive("themed-figure", ThemedFigureDirective)
    app.add_css_file("themed-figure.css")

    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
