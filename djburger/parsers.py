
# built-in
from functools import partial
from json import loads as _json


# BSON
try:
    from bson import loads as _bson
except:
    _bson = None


class Default(object):
    def __init__(self, method=None):
        self.method = method

    @staticmethod
    def _to_dict(query_dict):
        data = {}
        for k, v in query_dict.lists():
            data[k] = v[0] if len(v) == 1 else v
        return data

    def __call__(self, request):
        method = self.method or request.method.lower()
        if method == 'get':
            return self._to_dict(request.GET)
        else:
            return self._to_dict(request.POST)


class Base(object):
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
BSON = partial(Base, parser=_bson, encoding=None)
