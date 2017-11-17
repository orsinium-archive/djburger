# -*- coding: utf-8 -*-

# built-in
from collections import namedtuple
from functools import update_wrapper
# django
from django.views.generic import View


__all__ = ['Rule', 'rule', 'ViewBase']


Rule = namedtuple('Rule', [
    'decorators', 'validator', 'controller', 'post_validator',
    'error_serializer', 'response_error_serializer', 'serializer',
    ])


def rule(controller, serializers, decorators=None, validators=None):
    data = dict(decorators=decorators, controller=controller)

    if not validators:
        data['validator'], data['post_validator'] = None, None
    elif len(validators) == 1:
        data['validator'], data['post_validator'] = validators[0], None
    elif len(validators) == 2:
        data['validator'], data['post_validator'] = validators
    else:
        raise IndexError('Too many validators')

    if len(serializers) == 0:
        raise IndexError('Need 1-3 serializers')
    elif len(serializers) == 1:
        data['error_serializer'] = serializers[0]
        data['response_error_serializer'] = serializers[0]
        data['serializer'] = serializers[0]
    elif len(serializers) == 2:
        data['error_serializer'] = serializers[0]
        data['response_error_serializer'] = serializers[0]
        data['serializer'] = serializers[1]
    elif len(serializers) == 3:
        data['error_serializer'] = serializers[0]
        data['response_error_serializer'] = serializers[1]
        data['serializer'] = serializers[2]
    else:
        raise IndexError('Too many serializers')

    return Rule(**data)


class ViewBase(View):
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
        if not self.rule.error_serializer:
            raise NotImplementedError('error_serializer not implemented')
        return self.rule.error_serializer(
            request=self.request,
            validator=validator,
        )

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
            data = self.request.GET if self.request.method == 'get' else self.request.POST
        # get response from controller
        response = self.rule.controller(self.request, data, **self.kwargs)
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
        if not self.rule.response_error_serializer:
            raise NotImplementedError('response_error_serializer not implemented')
        return self.rule.response_error_serializer(
            request=self.request,
            validator=validator,
        )

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
        return self.rule.serializer(request=self.request, data=data)

    # send request and data into validator
    def get_validator_kwargs(self, data):
        '''
            Формирует парметры, передаваемые в валидаторы
        '''
        kwargs = super(ViewBase, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['data'] = data
        return kwargs
