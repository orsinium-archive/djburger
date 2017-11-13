import djburger
from . import controllers as c


class IndexView(djburger.ViewBase):
    rules = {
        'get': djburger.Rule(
            decorators=None,
            validator=None,
            error_serializer=None,
            controller=c.index_controller,
            post_validator=None,
            serializer=djburger.s.TemplateSerializer(
                template_name='index.html'
            ),
        ),
    }
