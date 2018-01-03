
class DjangoFormBase(object):
    def __init__(self, **kwargs):
        raise ImportError("Django is not installed yet")


class MarshmallowBase(object):
    def __init__(self, **kwargs):
        raise ImportError("Marshmallow is not installed yet")


class RESTFrameworkBase(object):
    def __init__(self, **kwargs):
        raise ImportError("Django REST Framework is not installed yet")


class PySchemes(object):
    def __init__(self, **kwargs):
        raise ImportError("PySchemes not installed yet")


def model_to_dict(*args, **kwargs):
    raise ImportError("Django is not installed yet")


class DjangoListView(object):
    def __init__(self, **kwargs):
        raise ImportError("Django is not installed yet")


class ValidationError(Exception):
    pass


class DjangoView(object):
    def as_view(self, **kwargs):
        raise ImportError(
            "Django is not installed yet. "
            "Please, install Django or make your own as_view method for ViewBase."
        )

    def __call__(self, *args, **kwargs):
        return self.dispatch(*args, **kwargs)


class QuerySet:
    pass
