# -*- coding: utf-8 -*-

# built-in
from functools import partial
# django
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render


class SerializerFactory(object):
    """Wrapper for using any function as serializer.
    """

    def __init__(self, serializer, content_name, request_name=None, names=None,
                 content=None, flat=False, **kwargs):
        """
        Args:
            serializer (callable): wrapped function for serializing
            content_name (str): key of data argument for serializer
            request_name (str): key of Request argument for serializer
            names (dict or None): dict of names. Keys:
                * data (default: "data"): name for data into content
                * errors (default: "errors"): name for errors into content
                * validator (default: None): name for validator into content.
                    If not setted, validator will not be passed into content.
            content (dict): default params for content.
            flat (bool): if True content contains only data or errors.
            **kwargs: some kwargs which content will be contain by default.
        """
        self.serializer = serializer
        self.content_name = content_name
        self.request_name = request_name
        self.names = names or {}
        self.content = content
        self.flat = flat
        self.kwargs = kwargs

    def __call__(self, request=None, data=None, validator=None):
        # content
        if self.flat:
            content = data or (validator and validator.errors)
        else:
            content = {}
            # init data for content if passed
            if self.content:
                content.update(self.content)
            # main data for content
            if data:
                content[self.names.get('data', 'data')] = data
            if validator and 'validator' in self.names:
                content[self.names['validator']] = validator
            if validator and validator.errors:
                content[self.names.get('errors', 'errors')] = validator.errors

        # kwargs for serialization function
        params = self.kwargs.copy()
        params[self.content_name] = content
        if self.request_name:
            params[self.request_name] = request

        # serialization
        return self.serializer(**params)


TemplateSerializerFactory = partial(
    SerializerFactory,
    serializer=render,
    content_name='context',
    request_name='request',
)
"""Serializer based on Django Templates
"""


class JSONSerializerFactory(SerializerFactory):
    """Serialize data into JSON
    """

    def __init__(self, flat=True, safe=False, **kwargs):
        """
        * Get all args of SerializerFactory.
        * Get all args of JsonResponse.
        * `flat` is True by default.
        * `safe` is False by default
        """
        super(JSONSerializerFactory, self).__init__(
            serializer=JsonResponse,
            content_name='data',
            flat=flat,
            safe=safe,
            **kwargs,
        )


class HTTPSerializerFactory(object):
    """Serialize data by HttpResponse.

    `data` can be only `str` or `bytes` type.
    """

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
    """Redirect to URL

    URL can be passed into initialization or into data (str).
    """

    def __init__(self, url=None):
        self.url = url

    def __call__(self, data=None, **kwargs):
        url = self.url or data
        return HttpResponseRedirect(url=url)


class ExceptionSerializer(object):
    """Raise Exception

    I'm reccomend use this serializer as ResponseErrorSerializer.
    Raised exception can be handled by decorators or loggers.
    """

    def __init__(self, exception=ValidationError):
        self.exception = exception

    def __call__(self, request, data=None, validator=None):
        if validator and validator.errors:
            raise self.exception(validator.errors)
        else:
            raise self.exception(data)
