
# built-in
import abc
from functools import partial
# external
from six import with_metaclass
# django
from django.forms import Form, ModelForm


class IValidator(with_metaclass(abc.ABCMeta)):

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
        self.request = request
        self.data_list = data
        self.kwargs = kwargs

    def is_valid(self):
        self.cleaned_data = []
        for data in self.data_list:
            validator = self.validator(data=data, **self.kwargs)
            if validator.is_valid()
                self.cleaned_data.append(validator.cleaned_data)
            else:
                self.errors = validator.errors
                return False
        return True


class DictValidator(ListValidator):
    '''
        Валидация значений словаря
    '''

    def is_valid(self):
        self.cleaned_data = {}
        for key, data in self.data_dict.items():
            validator = self.validator(data=data, **self.kwargs)
            if validator.is_valid()
                self.cleaned_data[key] = validator.cleaned_data
            else:
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
