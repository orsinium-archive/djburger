
# built-in
from functools import partial
from json import loads as _json

# project
from .datastructures import QueryDict


# BSON
try:
    from bson import loads as _bson
except ImportError:
    _bson = None


__all__ = [
    'MultiDict', 'DictList', 'DictMixed', 'Dict',
    'Base', 'JSON', 'BSON', 'Default',
]


class MultiDict(object):
    """Parse standart GET/POST query to MultiDict

    :param str method: optional method which will be forced for request

    :return: parsed data.
    :rtype: django.http.request.QueryDict
    """

    def __init__(self, method=None):
        self.method = method

    @staticmethod
    def convert(query_dict):
        return query_dict

    def __call__(self, request):
        method = (self.method or request.method).upper()
        # get parsed request body
        if method in ('GET', 'POST'):
            return self.convert(getattr(request, method))
        # parse request body if exists
        if request.body:
            return self.convert(QueryDict(request.body))
        # return GET params
        return self.convert(request.GET)


class DictList(MultiDict):
    """Parse standart GET/POST query to dict of lists

    :param str method: optional method which will be forced for request

    :return: parsed data.
    :rtype: Dict[list]
    """
    @staticmethod
    def convert(query_dict):
        return {k: v for k, v in query_dict.lists()}


class DictMixed(MultiDict):
    """Parse standart GET/POST query to dict of lists or values

    :param str method: optional method which will be forced for request

    :return: parsed data.
    :rtype: dict
    """
    @staticmethod
    def convert(query_dict):
        data = {}
        for k, v in query_dict.lists():
            data[k] = v[0] if len(v) == 1 else v
        return data


class Dict(MultiDict):
    """Parse standart GET/POST query to dict

    :param str method: optional method which will be forced for request

    :return: parsed data.
    :rtype: dict
    """
    @staticmethod
    def convert(query_dict):
        return dict(query_dict)


class Base(object):
    """Allow use any callable object as parser

    :param callable parser: callable object for parsing request body.
    :param str encoding: if not None body will be decoded from byte to str.
    :param \**kwargs: kwargs for parser.

    :return: parsed data.
    """

    def __init__(self, parser, encoding='utf-8', **kwargs):
        if not parser:
            raise ImportError('Selected parser is not installed yet')
        self.parser = parser
        self.encoding = encoding
        self.kwargs = kwargs

    def __call__(self, request):
        body = request.body
        body = body.decode(self.encoding) if self.encoding else body
        return self.parser(body, **self.kwargs)


JSON = partial(Base, parser=_json)
"""Parse JSON body.

:param str encoding: body encoding. UTF-8 by default.
:param \**kwargs: kwargs for `json.loads`.

:return: parsed data.
"""

BSON = partial(Base, parser=_bson, encoding=None)
"""Parse BSON body.

:param \**kwargs: kwargs for `bson.loads`.

:return: parsed data.
:rtype: dict

:raises ImportError: if `bson` module not installed yet.
"""


# alias
Default = MultiDict
