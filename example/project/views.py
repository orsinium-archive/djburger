import djburger


class IndexView(djburger.ViewBase):
    rules = {
        'get': djburger.Rule(
            decorators=None,
            validator=None,
            error_serializer=None,
            controller=lambda request, data, **kwargs: 'Hello, World!',
            post_validator=None,
            serializer=djburger.s.TemplateSerializer(
                template_name='index.html',
            ),
        ),
    }
