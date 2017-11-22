import djburger


class IndexView(djburger.ViewBase):
    rules = {
        'get': djburger.rule(
            controller=lambda request, data, **kwargs: 'Hello, World!',
            serializers=[
                djburger.s.TemplateSerializerFactory(template_name='index.html'),
            ]
        ),
    }
