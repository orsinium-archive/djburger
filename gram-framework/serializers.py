
# built-in
from functools import partial
# django
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render


class SerializerFactory(object):

    def __init__(self, serializer, content_name, request_name=None, names=None,
                 content=None, **kwargs):
        self.serializer = serializer
        self.content_name = content_name
        self.request_name = request_name
        self.names = names or {}
        self.content = content
        self.kwargs = kwargs

    def __call__(self, request=None, data=None, validator=None):
        # формируем контент (или контекст, если говорить о формах)
        content = {}
        # дополнительные данные для контента
        if self.content:
            content.update(self.content)
        # основные данные для контента
        if data:
            content[self.names.get('data', 'data')] = data
        if validator and 'validator' in self.names:
            content[self.names['validator'] = validator
        if validator.errors:
            content[self.names.get('errors', 'errors')] = validator.errors
        # параметры сериализатора
        params = self.kwargs.copy()
        params[content_name] = content
        if self.request_name and request:
            params[self.request_name] = request
        # сериализация
        return self.serializer(**params)


TemplateSerializer = partial(
    SerializerFactory,
    serializer=render,
    content_name='context',
    request_name='request',
)


JSONSerializer = partial(
    SerializerFactory,
    serializer=partial(serializers.serialize, 'json'),
    content_name='queryset',
)


XMLSerializer = partial(
    SerializerFactory,
    serializer=partial(serializers.serialize, 'xml'),
    content_name='queryset',
)


YAMLSerializer = partial(
    SerializerFactory,
    serializer=partial(serializers.serialize, 'yaml'),
    content_name='queryset',
)
