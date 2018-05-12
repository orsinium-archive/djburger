import djburger


class IndexView(djburger.ViewBase):
    rules = {
        'get': djburger.rule(
            controller=lambda request, data, **kwargs: 'Hello, World!',
            renderer=djburger.renderers.Template(template_name='index.html'),
        ),
    }
