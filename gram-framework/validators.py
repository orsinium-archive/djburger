
# built-in
import abc
from functools import partial
# external
from six import with_metaclass
# django
from django.forms import Form, ModelForm


class IValidator(with_metaclass(abc.ABCMeta)):
    '''
        Абстрактный базовый класс.
        Используйте его, чтобы не забыть реализовать что-то нужное.
    '''

    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def is_valid(self):
        pass

    @abc.abstractproperty
    def errors(self):
        pass

    @abc.abstractproperty
    def cleaned_data(self):
        pass


# Don't use IValidator here. It's raise conflict of metaclasses
class FormValidator(Form):
    '''
        Валидатор на основе Django-форм
    '''
    def __init__(self, request, **kwargs):
        self.request = request
        super(FormValidator, self).__init__(**kwargs)


class ModelFormValidator(ModelForm):
    '''
        Валидатор на основе модельных форм Django
    '''
    def __init__(self, request, **kwargs):
        self.request = request
        super(FormValidator, self).__init__(**kwargs)


class ListValidator(IValidator):
    '''
        Валидация элементов списка
    '''
    cleaned_data = None
    errors = None

    def __init__(self, validator, data, **kwargs):
        self.validator = validator
        self.data_list = data
        self.kwargs = kwargs

    def is_valid(self):
        self.cleaned_data = []
        for data in self.data_list:
            validator = self.validator(data=data, **self.kwargs)
            if validator.is_valid()
                self.cleaned_data.append(validator.cleaned_data)
            else:
                self.cleaned_data = []
                self.errors = validator.errors
                return False
        return True


class DictValidator(IValidator):
    '''
        Валидация значений словаря
    '''
    cleaned_data = None
    errors = None

    def __init__(self, validator, data, **kwargs):
        self.validator = validator
        self.data_dict = data
        self.kwargs = kwargs

    def is_valid(self):
        self.cleaned_data = {}
        for key, data in self.data_dict.items():
            validator = self.validator(data=data, **self.kwargs)
            if validator.is_valid()
                self.cleaned_data[key] = validator.cleaned_data
            else:
                self.cleaned_data = {}
                self.errors = validator.errors
                return False
        return True


class DictMixedValidatorFactory(IValidator):
    '''
        Валидация значений словаря различными валидаторами
    '''
    cleaned_data = None
    errors = None

    def __init__(self, validators, error_msg='Bad count of elements'):
        self.validators = validators
        self.error_msg = error_msg

    def __call__(self, data, **kwargs):
        self.data_dict = data
        self.kwargs = kwargs

    def is_valid(self):
        self.cleaned_data = {}

        if len(self.validators) != len(self.data_dict):
            self.errors = {'__all__': self.error_msg}
            return False

        for key, data in self.data_dict.items():
            validator = self.validators[key](data=data, **self.kwargs)
            if validator.is_valid()
                self.cleaned_data[key] = validator.cleaned_data
            else:
                self.cleaned_data = {}
                self.errors = validator.errors
                return False
        return True


# Валидация элементов списка с помощью Django-форм
ListFormValidator = partial(ListValidator, validator=FormValidator)
# Валидация значений словаря с помощью Django-форм
DictFormValidator = partial(DictValidator, validator=FormValidator)
# Валидация элементов списка с помощью модельных форм Django
ListModelFormValidator = partial(ListValidator, validator=ModelFormValidator)
# Валидация значений словаря с помощью модельных форм Django
DictModelFormValidator = partial(DictValidator, validator=ModelFormValidator)
