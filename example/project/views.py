import djburger


class IndexView(djburger.ViewBase):
    rules = {
        'get': djburger.rule(
            c=lambda request, data, **kwargs: 'Hello, World!',
            r=djburger.r.Template(template_name='index.html'),
        ),
    }
