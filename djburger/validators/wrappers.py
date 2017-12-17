'''Constructirs for validators

Use this classes as wrappers for non-djburger validators
'''

# project
from djburger.utils import safe_model_to_dict


__all__ = ['Form', 'Marshmallow', 'ModelForm', 'PySchemes', 'RESTFramework']


class _BaseWrapper(object):

    def __init__(self, validator):
        self.validator = validator

    def __call__(self, request, data, **kwargs):
        obj = self.validator(**kwargs)
        obj.request = request
        obj.data = safe_model_to_dict(data)
        # bound method to obj
        obj.is_valid = self.is_valid.__get__(obj)
        return obj


class Form(_BaseWrapper):
    """Wrapper for use Django Form (or ModelForm) as validator.
    """

    def __call__(self, request, **kwargs):
        obj = self.validator(**kwargs)
        obj.request = request
        return obj


class Marshmallow(_BaseWrapper):
    """Wrapper for use marshmallow scheme as validator.
    """

    # method binded to wrapped walidator
    @staticmethod
    def is_valid(self):
        self.cleaned_data, self.errors = self.load(self.data)
        return not self.errors


class PySchemes(_BaseWrapper):
    """Wrapper for use PySchemes as validator.
    """

    def __call__(self, request, data, **kwargs):
        self.request = request
        self.data = data
        return self

    def is_valid(self):
        self.cleaned_data = None
        self.errors = None
        try:
            self.cleaned_data = self.validator.validate(self.data)
        except Exception as e:
            self.errors = {'__all__': list(e.args)}
            return False
        return True


class RESTFramework(_BaseWrapper):
    """Wrapper for use Django REST Framework serializer as validator.
    """

    def __call__(self, request, data, **kwargs):
        data = safe_model_to_dict(data)
        obj = self.validator(data=data, **kwargs)
        obj.request = request
        # bound method to obj
        obj.is_valid = self.is_valid.__get__(obj)
        return obj

    # method binded to wrapped walidator
    @staticmethod
    def is_valid(self):
        result = super(self.__class__, self).is_valid()
        self.cleaned_data = self.validated_data
        return result


ModelForm = Form
