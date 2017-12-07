
# built-in
from json import loads as _json


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


class JSON(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, request):
        return _json(request.body, **self.kwargs)
