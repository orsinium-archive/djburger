# -*- coding: utf-8 -*-

# built-in
import abc
from collections import Iterator
# external
from six import with_metaclass
# django
from django.forms import Form, ModelForm


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
class FormValidator(Form):
    """Validator based on Django Forms.
    """

    def __init__(self, request, **kwargs):
        self.request = request
        super(FormValidator, self).__init__(**kwargs)


class ModelFormValidator(ModelForm):
    """Validator based on Django Model Forms.
    """

    def __init__(self, request, **kwargs):
        self.request = request
        super(ModelFormValidator, self).__init__(**kwargs)

    def save(self, *args, **kwargs):
        """All operations into validators must be idempotency.
        """
        raise NotImplementedError('Saving object from validator not allowed')


class _ListValidatorFactory(IValidator):
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


class _DictValidatorFactory(IValidator):
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


class DictMixedValidatorFactory(IValidator):
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


class TypeValidatorFactory(IValidator):
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


class LambdaValidatorFactory(IValidator):
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


class ChainValidatorFactory(IValidator):
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
IsBoolValidator = TypeValidatorFactory(bool)
IsIntValidator = TypeValidatorFactory(int)
IsFloatValidator = TypeValidatorFactory(float)
IsStrValidator = TypeValidatorFactory(str)
IsDictValidator = TypeValidatorFactory(dict)
IsListValidator = TypeValidatorFactory((list, tuple))
IsIterValidator = TypeValidatorFactory(Iterator)


# wrap ListValidator & DictValidator by type validation 

def ListValidatorFactory(validator): # noQA
    return ChainValidatorFactory([
        IsListValidator,
        _ListValidatorFactory(validator),
    ])

def DictValidatorFactory(validator): # noQA
    return ChainValidatorFactory([
        IsListValidator,
        _DictValidatorFactory(validator),
    ])


ListFormValidatorFactory = ListValidatorFactory(FormValidator)
"""Validate list elements by Django Forms
"""

DictFormValidatorFactory = DictValidatorFactory(FormValidator)
"""Validate dict values by Django Forms
"""

ListModelFormValidatorFactory = ListValidatorFactory(ModelFormValidator)
"""Validate list elements by Django Model Forms
"""

DictModelFormValidatorFactory = ListValidatorFactory(ModelFormValidator)
"""Validate dict values by Django Model Forms
"""
