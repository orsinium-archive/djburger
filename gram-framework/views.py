
# built-in
from collections import namedtuple, Iterable
# django
from django.views.generic import View


Rule = namedtuple('Rule', [
    'decorators', 'validator', 'error_serializer',
    'controller', 'post_validator', 'serializer',
    ])


__all__ = ['Rule', 'ViewBase']


def ViewBase(View):
    rules = None
    rule = None

    def dispatch(self, request, *args, **kwargs):
        '''
            1. Выбирает правило, соответствующее запросу
            2. Декорирует представление
            3. Вызывает метод validate
        '''
        method = request.method.lower()
        if method in self.rules:
            self.rule = self.rules[method]
        elif not self.rule:
            raise NotImplementedError('Please, set rule or rules attr')

        base = self.validate

        # decorators
        if self.rule.decorators:
            for decorator in self.rule.decorators:
                base = decorator(base)
            # take possible attributes set by decorators like csrf_exempt
            base = update_wrapper(base, self.validate, assigned=())

        return base(request, *args, **kwargs)

    # validator
    def validate(self, request, *args, **kwargs):
        '''
            1. Вызывает request_valid, если валидация пройдена или отсутствует
            2. Вызывает request_invalid, если валидация провалена
        '''
        # no validator
        if not self.rule.validator:
            return self.request_valid()
        # data for validation
        data = request.GET if self.request.method == 'get' else request.POST
        # validate
        validator = self.rule.validator(**self.get_validator_kwargs(data))
        if validator.is_valid():
            return self.request_valid(validator)
        else:
            return self.request_invalid(validator)

    # error_serializer
    def request_invalid(self, validator):
        '''
            Вызывает error_serializer, а если не задан - response.
            Передает в них параметр errors.
        '''
        resp = self.rule.error_serializer or self.rule.serializer
        return resp(errors=validator.errors)

    # controller
    def request_valid(self, validator=None):
        '''
            1. Получает response из controller
            2. Вызывает validate_response
        '''
        # get data for controller
        if validator:
            data = validator.cleaned_data
        else:
            # data for validation
            data = request.GET if self.request.method == 'get' else request.POST
        # get response from controller
        controller = self.rule.controller(self.request)
        response = controller(data, **self.kwargs)
        return self.validate_response(response)

    # post_validator
    def validate_response(self, response):
        '''
            1. Вызывает make_response, если post_validator отсутствует
            2. Проверяет данные с помощью post_validator
            3. Вызывает response_valid, если данные верные
            4. Вызывает response_invalid, если данные неверные
        '''
        if not self.rule.post_validator:
            return self.make_response(data=response)
        params = self.get_validator_kwargs(response)
        validator = self.rule.post_validator(**params)
        if validator.is_valid():
            return self.response_valid(validator)
        else:
            return self.response_invalid(validator)

    # bad response
    def response_invalid(self, validator):
        '''
            Вызывает request_invalid также, как при ошибке валидации запроса
        '''
        return self.request_invalid(validator)

    # response
    def response_valid(self, validator):
        '''
            Вызывает make_response
        '''
        return self.make_response(validator.cleaned_data)
    
    def make_response(self, data):
        '''
            Формирует response 
        '''
        return self.rule.serializer(data=data)

    # send request and data into validator
    def get_validator_kwargs(self, data):
        '''
            Формирует парметры, передаваемые в валидаторы
        '''
        kwargs = super(ValidatorMixin, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['data'] = data
        return kwargs
