'''Constructirs for validators

Use this classes for constructing your own validators.
'''

# built-in
from collections import Iterator
from functools import update_wrapper
from itertools import repeat
# project
from .bases import IValidator
from .wrappers import Form, ModelForm
from djburger.utils import safe_model_to_dict, is_django_installed

# Django
if is_django_installed:
    from django.db.models.query import QuerySet as _QuerySet
    from django.db.models import Model as _Model
    from django.forms.models import model_to_dict
    from django.http.request import QueryDict as _QueryDict
else:
    from djburger.mocks import model_to_dict, QuerySet as _QuerySet
    _Model = _QuerySet
    _QueryDict = dict


# PySchemes
try:
    from pyschemes import Scheme as _PySchemesScheme
except ImportError:
    from djburger.mocks import PySchemes as _PySchemesScheme


__all__ = [
    'Chain',
    'Dict', 'DictForm', 'DictMixed', 'DictModelForm',
    'IsBool', 'IsDict', 'IsFloat', 'IsInt', 'IsIter', 'IsList', 'IsStr',
    'Lambda', 'List', 'ListForm', 'ListModelForm',
    'ModelInstance',
    'PySchemes',
    'Type',
    'QuerySet',
]


class _PySchemes(_PySchemesScheme):
    """Validate data by PySchemes.

    :param scheme: validation scheme for pyschemes.
    """

    def __call__(self, request, data, **kwargs):
        self.request = request
        self.data = safe_model_to_dict(data)
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


class _List(IValidator):
    """Validate data list.

    :param validators: if passed only one validator it's be applied to each list element.
        One validator will be applyed to one element sequentionaly otherwise.
    """

    cleaned_data = None
    errors = None

    def __init__(self, validator, *validators):
        if validators:
            self.validators = [validator] + list(validators)
        else:
            self.validators = repeat(validator)

    def __call__(self, data, **kwargs):
        self.data_list = data
        self.kwargs = kwargs
        return self

    def is_valid(self):
        self.cleaned_data = []
        for data, validator in zip(self.data_list, self.validators):
            validator = validator(data=data, **self.kwargs)
            if validator.is_valid():
                self.cleaned_data.append(validator.cleaned_data)
            else:
                self.cleaned_data = []
                self.errors = validator.errors
                return False
        return True


class _Dict(IValidator):
    """Validate data dict

    :param validator: walidator which be applyed to all values of dict.
    """

    cleaned_data = None
    errors = None

    def __init__(self, validator):
        self.validator = validator

    def __call__(self, data, **kwargs):
        self.data_dict = data
        self.kwargs = kwargs
        return self

    def is_valid(self):
        self.cleaned_data = {}
        for key, data in self.data_dict.items():
            validator = self.validator(data=data, **self.kwargs)
            if validator.is_valid():
                self.cleaned_data[key] = validator.cleaned_data
            else:
                self.cleaned_data = {}
                self.errors = validator.errors
                return False
        return True


class _DictMixed(IValidator):
    """Validate dict keys by multiple validators

    :param dict validators: walidator which be applyed to all values of dict.
    :param str policy: policy if validator for data not found:
        "error" - add error into `errors` attr and return False.
        "except" - raise KeyError exception.
        "ignore" - add source value into cleaned_data.
        "drop" - drop this value and continue.
    """

    cleaned_data = None
    errors = None
    error_msg = 'No validator for {}'

    def __init__(self, validators, policy='error'):
        self.validators = validators
        if policy not in ('error', 'except', 'ignore', 'drop'):
            raise KeyError(
                'Bad policy value.'
                'Allowed "error", "except", "ignore" or "drop".'
            )
        self.policy = policy

    def __call__(self, data, **kwargs):
        self.data_dict = data
        self.kwargs = kwargs
        return self

    def is_valid(self):
        self.cleaned_data = {}

        for key, data in self.data_dict.items():
            if key in self.validators:  # founded
                validator = self.validators[key](data=data, **self.kwargs)
            elif self.policy == 'error':
                self.errors = {'__all__': [self.error_msg.format(key)]}
                return False
            elif self.policy == 'except':
                raise KeyError(self.error_msg.format(key))
            elif self.policy == 'ignore':
                self.cleaned_data[key] = data
                continue
            else:  # drop
                continue

            if validator.is_valid():
                self.cleaned_data[key] = validator.cleaned_data
            else:
                self.cleaned_data = {}
                self.errors = validator.errors
                return False
        return True


class Type(IValidator):
    """Validate data type

    :param type data_type: required type of data.
    :param str error_msg: template for error message.
    """
    cleaned_data = None
    errors = None

    def __init__(self, data_type,
                 error_msg='Invalid data type: {}. Required {}.'):
        self.data_type = data_type
        self.error_msg = error_msg

    def __call__(self, data, **kwargs):
        self.data = data
        return self

    def is_valid(self):
        if type(self.data_type) is type:
            # strict validation for types
            passed = type(self.data) is self.data_type
        else:
            # validation with inheritance for list of types and other cases.
            passed = isinstance(self.data, self.data_type)

        # valid
        if passed:
            self.cleaned_data = self.data
            return True

        # invalid
        self.errors = {'__all__': [
            self.error_msg.format(
                type(self.data).__name__,
                getattr(self.data_type, '__name__', self.data_type),
            ),
        ]}
        return False


class Lambda(IValidator):
    """Validate data by lambda expression.

    :param callable key: lambda, function or other callable object
        which get data and return bool result (True if valid).
    """
    cleaned_data = None
    errors = None

    def __init__(self, key, error_msg='Custom validation is failed'):
        self.key = key
        self.error_msg = error_msg

    def __call__(self, data, **kwargs):
        self.data = data
        return self

    def is_valid(self):
        if self.key(self.data):
            self.cleaned_data = self.data
            return True

        self.errors = {'__all__': [self.error_msg]}
        return False


class Clean(IValidator):
    """Clean data by lambda expression.

    Doesn't catch any exceptions. Always use validation before.

    :param callable key: lambda, function or other callable object
        which get data and return cleaned result.
    """
    cleaned_data = None
    errors = None

    def __init__(self, key):
        self.key = key

    def __call__(self, data, **kwargs):
        self.data = data
        return self

    def is_valid(self):
        self.cleaned_data = self.key(self.data)
        return True


class Chain(IValidator):
    """Validate data by validators chain (like reduce function).

    Calls the validators in order, passing in each subsequent cleaned data
    from the previous one.

    :param list validators: list of validators.
    """
    cleaned_data = None
    errors = None

    def __init__(self, *validators):
        if len(validators) == 1:
            validators = validators[0]
        self.validators = validators

    def __call__(self, data, **kwargs):
        self.data = data
        self.kwargs = kwargs
        return self

    def is_valid(self):
        for validator in self.validators:
            validator = validator(data=self.data, **self.kwargs)
            if validator.is_valid():
                self.data = validator.cleaned_data
            else:
                self.errors = validator.errors
                return False
        self.cleaned_data = self.data
        return True


class Or(IValidator):
    """Validate data by validators (like `any` function).

    Calls the validators in order,
    return cleaned_data from first successfull validation
    or errors from last validator

    :param list validators: list of validators.
    """
    cleaned_data = None
    errors = None

    def __init__(self, *validators):
        if len(validators) == 1:
            validators = validators[0]
        self.validators = validators

    def __call__(self, data, **kwargs):
        self.data = data
        self.kwargs = kwargs
        return self

    def is_valid(self):
        for validator in self.validators:
            validator = validator(data=self.data, **self.kwargs)
            if validator.is_valid():
                self.cleaned_data = validator.cleaned_data
                return True
            else:
                self.errors = validator.errors
        return False


class _ModelInstance(IValidator):
    """Validate model instance and convert it to dict.

    Doesn't require initialization.
    """
    cleaned_data = None
    errors = None

    def __init__(self, data, **kwargs):
        self.data = data
        self.kwargs = kwargs

    def is_valid(self):
        if isinstance(self.data, _Model):
            self.cleaned_data = model_to_dict(self.data)
        else:
            self.cleaned_data = self.data
        return True


# -- SUBVALIDATORS -- #


ModelInstance = Chain([
    Type(_Model),
    _ModelInstance,
])
"""Validate model instance and convert it to dict.

Doesn't require initialization.
"""


QuerySet = Chain([
    Type(_QuerySet),
    _List(ModelInstance),
])
"""Validate queryset and convert each object in it to dict.

Doesn't require initialization.
"""


# data types validation
IsBool = Type(bool)
IsInt = Type(int)
IsFloat = Type(float)
IsStr = Type(str)
IsDict = Type((dict, _QueryDict))
IsList = Type((list, tuple))
IsIter = Type(Iterator)


# wrap ListValidator & DictValidator by type validation

def List(validator): # noQA
    return Chain([
        IsList,
        _List(validator),
    ])

def Dict(validator): # noQA
    return Chain([
        IsDict,
        _Dict(validator),
    ])

def DictMixed(validators, policy='error'): # noQA
    return Chain([
        IsDict,
        _DictMixed(validators, policy=policy),
    ])


def PySchemes(scheme, policy='error'): # noQA
    if scheme and type(scheme) is dict:
        scheme = {k: PySchemes(v, policy) for k, v in scheme.items()}
        return Chain(
            Type((dict, _Model)),
            _ModelInstance,  # convert models to dict if possible
            _DictMixed(scheme, policy),
        )
    elif scheme and type(scheme) is list:
        scheme = [PySchemes(v) for v in scheme]
        return Chain(
            Type((list, _QuerySet)),
            _List(_ModelInstance),
            # ^ convert querysets to list of dicts if possible
            _List(*scheme),
        )
    else:
        return _PySchemes(scheme)


def ListForm(form): # noQA
    """Validate list elements by Django Forms
    """
    return List(Form(form))


def DictForm(form): # noQA
    """Validate dict values by Django Forms
    """
    return Dict(Form(form))

def ListModelForm(form): # noQA
    """Validate list elements by Django Model Forms
    """
    return List(ModelForm(form))

def DictModelForm(form): # noQA
    """Validate dict values by Django Model Forms
    """
    return Dict(ModelForm(form))


# aliases
Any = OR = Or
All = Chain


# copy docstrings
List = update_wrapper(List, _List)
Dict = update_wrapper(Dict, _Dict)
DictMixed = update_wrapper(DictMixed, _DictMixed)
PySchemes = update_wrapper(PySchemes, _PySchemes)
