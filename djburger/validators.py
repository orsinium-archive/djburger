
# built-in
import abc
from collections import Iterator
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

    def save(self, *args, **kwargs):
        raise NotImplementedError('Saving object from validator not allowed')


class _ListValidator(IValidator):
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
            if validator.is_valid():
                self.cleaned_data.append(validator.cleaned_data)
            else:
                self.cleaned_data = []
                self.errors = validator.errors
                return False
        return True


class _DictValidator(IValidator):
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
            if validator.is_valid():
                self.cleaned_data[key] = validator.cleaned_data
            else:
                self.cleaned_data = {}
                self.errors = validator.errors
                return False
        return True


class DictMixedValidatorFactory(IValidator):
    '''
        Валидация значений словаря различными валидаторами

        validators - словарь валидаторов, где ключ совпадает с ключом
            валидируемых данных
        validate_all - если отсутствует валидатор для какого-либо ключа, то...
            True - возвращает ошибку валидации
            False - Добавляет в результат данные без валидации
    '''
    cleaned_data = None
    errors = None
    error_msg = 'No validator for {}'

    def __init__(self, validators, validate_all=True):
        self.validators = validators
        self.validate_all = validate_all

    def __call__(self, data, **kwargs):
        self.data_dict = data
        self.kwargs = kwargs
        return self

    def is_valid(self):
        self.cleaned_data = {}

        for key, data in self.data_dict.items():
            if key in self.validators:
                validator = self.validators[key](data=data, **self.kwargs)
            elif self.validate_all:
                self.errors = {'__all__': [self.error_msg.format(key)]}
                return False
            else:
                self.cleaned_data[key] = data
                continue

            if validator.is_valid():
                self.cleaned_data[key] = validator.cleaned_data
            else:
                self.cleaned_data = {}
                self.errors = validator.errors
                return False
        return True


class TypeValidator(IValidator):
    '''
        Проверяет, что результат является объектом заданного типа
    '''
    cleaned_data = None
    errors = None
    error_msg = 'Invalid data format: {}. Required {}.'

    def __init__(self, data, data_type, **kwargs):
        self.data = data
        self.data_type = data_type

    def is_valid(self):
        if type(self.data_type) is type:
            # строгая валидация для типов данных
            passed = type(self.data) is self.data_type
        else:
            # валидация с наследованием для списка типов
            # и других случаев
            passed = isinstance(self.data, self.data_type)

        if passed:
            self.cleaned_data = self.data
            return True

        self.errors = {'__all__': [
            self.error_msg.format(
                type(self.data).__name__,
                getattr(self.data_type, '__name__', self.data_type),
            ),
        ]}
        return False


class LambdaValidatorFactory(IValidator):
    '''
        Проверяет данные с помощью заданного выражения
    '''
    cleaned_data = None
    errors = None
    error_msg = 'Custom validation not passed'

    def __init__(self, key):
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


class ChainValidator(IValidator):
    '''
        Вызывает валидаторы по порядку, передавая в каждый следующий
        очищенные данные из предыдущего.
    '''
    cleaned_data = None
    errors = None

    def __init__(self, data, validators, **kwargs):
        self.data = data
        self.validators = validators
        self.kwargs = kwargs

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


# Валидация типов данных
IsBoolValidator = partial(TypeValidator, data_type=bool)
IsIntValidator = partial(TypeValidator, data_type=int)
IsFloatValidator = partial(TypeValidator, data_type=float)
IsStrValidator = partial(TypeValidator, data_type=str)
IsDictValidator = partial(TypeValidator, data_type=dict)
IsListValidator = partial(TypeValidator, data_type=(list, tuple))
IsIterValidator = partial(TypeValidator, data_type=Iterator)

# Цепляем к ListValidator и DictValidator проверку типов данных на входе
ListValidator = partial(ChainValidator, validators=[IsListValidator, _ListValidator])
DictValidator = partial(ChainValidator, validators=[IsDictValidator, _DictValidator])

# Валидация элементов списка с помощью Django-форм
ListFormValidator = partial(ListValidator, validator=FormValidator)
# Валидация значений словаря с помощью Django-форм
DictFormValidator = partial(DictValidator, validator=FormValidator)

# Валидация элементов списка с помощью модельных форм Django
ListModelFormValidator = partial(ListValidator, validator=ModelFormValidator)
# Валидация значений словаря с помощью модельных форм Django
DictModelFormValidator = partial(DictValidator, validator=ModelFormValidator)
