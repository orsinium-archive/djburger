'''Constructirs for validators

Use this classes as wrappers for non-djburger validators
'''


class Form(object):

    def __init__(self, validator):
        self.validator = validator

    def __call__(self, request, **kwargs):
        obj = self.validator(**kwargs)
        obj.request = request
        return obj


class Marshmallow(object):
    def __init__(self, validator):
        self.validator = validator

    def __call__(self, request, data, **kwargs):
        obj = self.validator(**kwargs)
        obj.request = request
        obj.data = data
        # bound method to obj
        obj.is_valid = self.is_valid.__get__(obj)
        return obj

    # method binded to wrapped walidator
    @staticmethod
    def is_valid(self):
        self.cleaned_data, self.errors = self.load(self.data)
        return not self.errors


class PySchemes(object):
    def __init__(self, validator):
        self.validator = validator

    def __call__(self, request, data, **kwargs):
        obj = self.validator(**kwargs)
        obj.request = request
        obj.data = data
        # bound method to obj
        obj.is_valid = self.is_valid.__get__(obj)
        return obj

    @staticmethod
    def is_valid(self):
        self.cleaned_data = None
        self.errors = None
        try:
            self.cleaned_data = self.validate(self.data)
        except Exception as e:
            self.errors = {'__all__': list(e.args)}
            return False
        return True


ModelForm = Form
