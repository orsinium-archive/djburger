
# built-in
import abc
from collections import Iterator
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
        super(ModelFormValidator, self).__init__(**kwargs)

    def save(self, *args, **kwargs):
        raise NotImplementedError('Saving object from validator not allowed')


class _ListValidatorFactory(IValidator):
    '''
        Валидация элементов списка
    '''
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
    '''
        Валидация значений словаря
    '''
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
    '''
        Валидация значений словаря различными валидаторами

        validators - словарь валидаторов, где ключ совпадает с ключом
            валидируемых данных
        policy - если отсутствует валидатор для какого-либо ключа, то...
            error - возвращает ошибку валидации
            ignore - Добавляет в результат данные без валидации
            drop - Удаляет данные
    '''
    cleaned_data = None
    errors = None
    error_msg = 'No validator for {}'

    def __init__(self, validators, policy='drop'):
        self.validators = validators
        if policy not in ('error', 'ignore', 'drop'):
            raise KeyError('Bad policy value. Allowe "error", "except" or "drop".')
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
    '''
        Проверяет, что результат является объектом заданного типа
    '''
    cleaned_data = None
    errors = None
    error_msg = 'Invalid data format: {}. Required {}.'

    def __init__(self, data_type):
        self.data_type = data_type

    def __call__(self, data, **kwargs):
        self.data = data
        return self

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


class ChainValidatorFactory(IValidator):
    '''
        Вызывает валидаторы по порядку, передавая в каждый следующий
        очищенные данные из предыдущего.
    '''
    cleaned_data = None
    errors = None

    def __init__(self, validators):
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


# Валидация типов данных
IsBoolValidator = TypeValidatorFactory(bool)
IsIntValidator = TypeValidatorFactory(int)
IsFloatValidator = TypeValidatorFactory(float)
IsStrValidator = TypeValidatorFactory(str)
IsDictValidator = TypeValidatorFactory(dict)
IsListValidator = TypeValidatorFactory((list, tuple))
IsIterValidator = TypeValidatorFactory(Iterator)


# Цепляем к ListValidator и DictValidator проверку типов данных на входе

def ListValidatorFactory(validator): # noQA
    return ChainValidatorFactory([IsListValidator, _ListValidatorFactory(validator)])

def DictValidatorFactory(validator): # noQA
    return ChainValidatorFactory([IsListValidator, _DictValidatorFactory(validator)])


# Валидация элементов списка с помощью Django-форм
ListFormValidatorFactory = ListValidatorFactory(FormValidator)
# Валидация значений словаря с помощью Django-форм
DictFormValidatorFactory = DictValidatorFactory(FormValidator)

# Валидация элементов списка с помощью модельных форм Django
ListModelFormValidatorFactory = ListValidatorFactory(ModelFormValidator)
# Валидация значений словаря с помощью модельных форм Django
DictModelFormValidatorFactory = ListValidatorFactory(ModelFormValidator)
