'''Constructirs for validators

Use this classes for constructing your own validators.
'''

# built-in
import abc
from collections import Iterator
# external
from django.forms import Form as _Form, ModelForm as _ModelForm
from six import with_metaclass
# project
from .bases import Form, IValidator, ModelForm


__all__ = [
    'Chain', 
    'Dict', 'DictForm', 'DictMixed', 'DictModelForm', 
    'IsBool', 'IsDict', 'IsFloat', 'IsInt', 'IsIter', 'IsList', 'IsStr',
    'Lambda', 'List', 'ListForm', 'ListModelForm',
    'Type',
]


class _List(IValidator):
    """Validate data list
    """

    cleaned_data = None
    errors = None

    def __init__(self, validator):
        self.validator = validator

    def __call__(self, data, **kwargs):
        self.data_list = data
        self.kwargs = kwargs
        return self

    def is_valid(self):
        self.cleaned_data = []
        for data in self.data_list:
            validator = self.validator(data=data, **self.kwargs)
            if validator.is_valid():
                self.cleaned_data.append(validator.cleaned_data)
            else:
                self.cleaned_data = []
                self.errors = validator.errors
                return False
        return True


class _Dict(IValidator):
    """Validate data dict
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


class DictMixed(IValidator):
    """Validate dict keys by multiple validators
    """

    cleaned_data = None
    errors = None
    error_msg = 'No validator for {}'

    def __init__(self, validators, policy='error'):
        """
        Args:
            validators (dict): validators for data.
            policy (str): policy if validator for data not found:
                "error" - add error into `errors` attr and return False.
                "except" - raise KeyError exception.
                "ignore" - add source value into cleaned_data.
                "drop" - drop this value and continue.
        """
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
    """
    cleaned_data = None
    errors = None
    error_msg = 'Invalid data format: {}. Required {}.'

    def __init__(self, data_type):
        """
        Args:
            data_type: required type of data.
        """
        self.data_type = data_type

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
    """
    cleaned_data = None
    errors = None
    error_msg = 'Custom validation not passed'

    def __init__(self, key):
        """
        Args:
            key (callable): lambda, function or other callable object
                which get data and return bool result (True if valid).
        """
        self.key = key

    def __call__(self, data, **kwargs):
        self.data = data
        return self

    def is_valid(self):
        if self.key(self.data):
            self.cleaned_data = self.data
            return True

        self.errors = {'__all__': [self.error_msg]}
        return False


class Chain(IValidator):
    """Validate data by validators chain (like reduce function).

    Calls the validators in order, passing in each subsequent cleaned data
    from the previous one.
    """
    cleaned_data = None
    errors = None

    def __init__(self, validators):
        """
        Args:
            validators (list): list of validators
        """
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


# data types validation
IsBool = Type(bool)
IsInt = Type(int)
IsFloat = Type(float)
IsStr = Type(str)
IsDict = Type(dict)
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


ListForm = List(Form)
"""Validate list elements by Django Forms
"""

DictForm = Dict(Form)
"""Validate dict values by Django Forms
"""

ListModelForm = List(ModelForm)
"""Validate list elements by Django Model Forms
"""

DictModelForm = Dict(ModelForm)
"""Validate dict values by Django Model Forms
"""
