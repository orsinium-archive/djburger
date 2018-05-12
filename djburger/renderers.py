# built-in
from functools import partial
# project
from .exceptions import ValidationError
from .utils import is_django_installed


# Django
if is_django_installed:
    from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
    from django.shortcuts import render
else:
    from .mocks import model_to_dict as render
    HttpResponseRedirect = JsonResponse = HttpResponse = render


# PyYAML
try:
    import yaml as _yaml
except ImportError:
    _yaml = None


# BSON
try:
    import bson as _bson
except ImportError:
    _bson = None


# tablib
try:
    from tablib import Dataset as _Tablib
except ImportError:
    _Tablib = None # noQA


__all__ = [
    'BSON', 'Base', 'BaseWithHTTP',
    'Exception',
    'HTTP',
    'JSON',
    'RESTFramework',
    'Redirect',
    'Tablib', 'Template',
    'YAML',
]


class Base(object):
    """Wrapper for using any function as renderer.

    :param callable renderer: function for rendering.
    :param str content_name: keyword of data argument for renderer.
    :param str request_name: keyword of Request argument for renderer.
    :param dict names: dict of names. Keys:
        * data (default: "data"): name for data into content.
        * errors (default: "errors"): name for errors into content.
        * validator (default: None): name for validator into content. \
            If not setted, validator will not be passed into content.
    :param dict content: default params for content.
    :param bool flat: if True content contains only data or errors.
    :param \**kwargs: some kwargs which will be passed to renderer.

    :return: rendered response.
    :rtype: django.http.HttpResponse
    """

    def __init__(self, renderer, content_name, request_name=None, names=None,
                 content=None, flat=False, **kwargs):
        self.renderer = renderer
        self.content_name = content_name
        self.request_name = request_name
        self.names = names or {}
        self.content = content
        self.flat = flat
        self.kwargs = kwargs

    def __call__(self, request=None, data=None, validator=None, status_code=None):
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

        # kwargs for rendering function
        params = self.kwargs.copy()
        params[self.content_name] = content
        if self.request_name:
            params[self.request_name] = request

        # rendering
        response = self.renderer(**params)
        if status_code:
            response.status_code = status_code
        return response


class BaseWithHTTP(Base):
    """Base class wrapped by HttpResponse

    :param \**kwargs: all kwargs of djburger.renderers.Base.
    """

    def set_http_kwargs(self, **kwargs):
        """Set kwargs for HttpResponse

        :param \**kwargs: all kwargs of HttpResponse.

        :return: self. Allow use chain.
        :rtype: BaseWithHTTP
        """
        self.http_kwargs = kwargs
        return self

    def __call__(self, status_code=None, **kwargs):
        http_kwargs = self.http_kwargs.copy()
        if status_code:
            http_kwargs['status_code'] = status_code
        content = super(BaseWithHTTP, self).__call__(**kwargs)
        return HttpResponse(content, **http_kwargs)


Template = partial(
    Base,
    renderer=render,
    content_name='context',
    request_name='request',
)
"""Serializer based on Django Templates
"""


class JSON(Base):
    """Serialize data into JSON
    """

    def __init__(self, flat=True, safe=False, **kwargs):
        """
        * Get all args of SerializerFactory.
        * Get all args of JsonResponse.
        * `flat` is True by default.
        * `safe` is False by default
        """
        super(JSON, self).__init__(
            renderer=JsonResponse,
            content_name='data',
            flat=flat,
            safe=safe,
            **kwargs)


class HTTP(object):
    """Render data by HttpResponse.

    `data` can be only `str` or `bytes` type.
    """

    def __init__(self, status_code=200, **kwargs):
        self.status_code = status_code
        self.kwargs = kwargs

    def __call__(self, request=None, data=None, validator=None, status_code=None):
        if not isinstance(data, (str, bytes, int, float, list)):
            t = type(data)
            if hasattr(t, '__name__'):
                t = t.__name__
            raise ValueError("Bad data format: {}".format(t))
        response = HttpResponse(data, **self.kwargs)
        response.status_code = status_code or self.status_code
        return response


class Redirect(object):
    """Redirect to URL

    URL can be passed by initialization or as data (str).

    :param url: url for redirect.

    :return: rendered redirect response.
    :rtype: django.http.HttpResponseRedirect
    """

    def __init__(self, url=None):
        self.url = url

    def __call__(self, data=None, **kwargs):
        url = self.url or data
        return HttpResponseRedirect(redirect_to=url)


class Exception(object): # noQA
    """Raise Exception

    We are recommend use this renderer as `postrenderer`.
    Raised exception can be handled by decorators or loggers.

    :param exception: exception for raising.
    """

    def __init__(self, exception=ValidationError):
        self.exception = exception

    def __call__(self, request=None, data=None, validator=None, status_code=None):
        if validator and validator.errors:
            raise self.exception(validator.errors)
        else:
            raise self.exception(data)


class RESTFramework(BaseWithHTTP):
    """Wrapper for renderers from Django REST Framework
    """

    def __init__(self, renderer, flat=True, **kwargs):
        # initialize renderer
        if type(renderer) is type:
            renderer = renderer()
        self.http_kwargs = {}
        super(RESTFramework, self).__init__(
            renderer=renderer.render,
            content_name='data',
            flat=flat,
            **kwargs
        )


class YAML(BaseWithHTTP):
    """Render into YAML format by PyYAML

    :return: rendered response.
    :rtype: django.http.HttpResponse
    """

    def __init__(self, flat=True, **kwargs):
        if not _yaml:
            raise ImportError('PyYAML is not installed yet')
        self.http_kwargs = {}
        super(YAML, self).__init__(
            renderer=_yaml.dump,
            content_name='data',
            flat=flat,
            **kwargs
        )


class BSON(BaseWithHTTP):
    """Render into BSON format by BSON package

    :return: rendered response.
    :rtype: django.http.HttpResponse
    """

    def __init__(self, flat=True, **kwargs):
        if not _yaml:
            raise ImportError('BSON is not installed yet')
        self.http_kwargs = {}
        super(BSON, self).__init__(
            renderer=_bson.dumps,
            content_name='obj',
            flat=flat,
            **kwargs
        )


class Tablib(BaseWithHTTP):
    """Render into multiple formats by tablib

    :param ext: extension for rendering by Tablib.
    :param headers: table headers.

    :return: rendered response.
    :rtype: django.http.HttpResponse
    """

    def __init__(self, ext, headers=None, **kwargs):
        if not _Tablib:
            raise ImportError('Tablib is not installed yet')
        self.http_kwargs = {}
        self.ext = ext
        self.headers = headers
        super(Tablib, self).__init__(
            renderer=self.render,
            content_name='data',
            flat=True,
            **kwargs
        )

    def render(self, data):
        dataset = _Tablib(*data, headers=self.headers)
        return dataset.export(self.ext)
