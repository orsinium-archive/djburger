'''Base classes for validators

Use this classes as base class for your own validators.
'''

# built-in
import abc
from collections import Iterator
# external
from django.forms import Form as _Form, ModelForm as _ModelForm
from six import with_metaclass


__all__ = ['Form', 'IValidator', 'Marshmallow', 'ModelForm', 'PySchemes']


# marshmallow
try:
    from marshmallow import Schema as _MarshmallowSchema
except ImportError:
    class _MarshmallowSchema(object):
        def __init__(self, **kwargs):
            raise ImportError("Marshmallow not installed yet")


# PySchemes
try:
    from pyschemes import _PySchemesScheme
except ImportError:
    class _PySchemesScheme(object):
        def __init__(self, **kwargs):
            raise ImportError("PySchemes not installed yet")


class IValidator(with_metaclass(abc.ABCMeta)):
    """Abstract base class for validators.
    """

    @abc.abstractmethod
    def __init__(self):
        """
        Args:
            request - Request object
            **kwargs - all kwargs of Django Forms.
        """
        pass

    @abc.abstractmethod
    def is_valid(self):
        """Validate and clean data.

        1. Set `cleaned_data` and return True if data is valid
        2. Set `errors` and return False otherwise.

        Returns:
            True: data is valid
            False: data is invalid
        """
        pass

    @abc.abstractproperty
    def errors(self):
        """Errors dict. Set by `is_valid` method.

        key: name of invalid field or `__all__`.
        value: list of errors strings.
        """
        pass

    @abc.abstractproperty
    def cleaned_data(self):
        """Cleaned data dict (or other type). Set by `is_valid` method.
        """
        pass


# Don't use IValidator here. It's raise conflict of metaclasses
class Form(_Form):
    """Validator based on Django Forms.
    """

    def __init__(self, request, **kwargs):
        self.request = request
        super(_Form, self).__init__(**kwargs)


class ModelForm(_ModelForm):
    """Validator based on Django Model Forms.
    """

    def __init__(self, request, **kwargs):
        self.request = request
        super(ModelForm, self).__init__(**kwargs)

    def save(self, *args, **kwargs):
        """All operations into validators must be idempotency.
        """
        raise NotImplementedError('Saving object from validator not allowed')


class Marshmallow(_MarshmallowSchema):

    def __init__(self, request, data, **kwargs):
        self.request = request
        self.data = data
        super(Marshmallow, self).__init__(**kwargs)

    def is_valid(self):
        self.cleaned_data, self.errors = self.load(self.data)
        return not self.errors


class PySchemes(_PySchemesScheme):

    def __call__(self, request, data, **kwargs):
        self.request = request
        self.data = data
        return self

    def is_valid(self):
        self.cleaned_data = None
        self.errors = None
        try:
            self.cleaned_data = self.validate(self.data)
        except Exception as e:
            self.errors = {'__all__': list(e.args)}
            return False
        return True
