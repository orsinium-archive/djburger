# -*- coding: utf-8 -*-

# built-in
from functools import partial
# django
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
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

    def __call__(self, request, data=None, validator=None):
        # формируем контент (или контекст, если говорить о формах)
        content = {}
        # дополнительные данные для контента
        if self.content:
            content.update(self.content)
        # основные данные для контента
        if data:
            content[self.names.get('data', 'data')] = data
        if validator and 'validator' in self.names:
            content[self.names['validator']] = validator
        if validator and validator.errors:
            content[self.names.get('errors', 'errors')] = validator.errors
        # параметры сериализатора
        params = self.kwargs.copy()
        params[self.content_name] = content
        if self.request_name:
            params[self.request_name] = request
        # сериализация
        return self.serializer(**params)


TemplateSerializerFactory = partial(
    SerializerFactory,
    serializer=render,
    content_name='context',
    request_name='request',
)


class JSONSerializerFactory(object):

    def __init__(self, flat=True, safe=False, data_name='data', errors_name='errors'):
        self.flat = flat
        self.safe = safe
        self.data_name = data_name
        self.errors_name = errors_name

    def __call__(self, request=None, data=None, validator=None):
        if self.flat:
            content = data or (validator and validator.errors)
        else:
            content = {}
            if data:
                content[self.data_name] = data
            if validator and validator.errors:
                content[self.errors_name] = validator.errors
        return JsonResponse(content, safe=self.safe)


class HTTPSerializerFactory(object):

    def __init__(self, status_code=200, **kwargs):
        self.status_code = status_code
        self.kwargs = kwargs

    def __call__(self, request=None, data=None, validator=None):
        if data is None:
            raise ValueError("Data can't be None in HTTPSerializerFactory")
        if type(data) is str:
            data = data.encode()
        response = HttpResponse(data, **self.kwargs)
        response.status_code = self.status_code
        return response


class RedirectSerializer(object):

    def __init__(self, url=None):
        self.url = url

    def __call__(self, data=None, **kwargs):
        url = self.url or data
        return HttpResponseRedirect(url=url)


class ExceptionSerializer(object):
    '''
        Поднимает исключение, чтобы его можно было обработать
        на уровне логеров Django.
    '''

    def __init__(self, exception=ValidationError):
        self.exception = exception

    def __call__(self, request, data=None, validator=None):
        if validator and validator.errors:
            raise self.exception(validator.errors)
        else:
            raise self.exception(data)
