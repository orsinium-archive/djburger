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
    """Factory of Rule objects
    """
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
    """Base views for DjBurger usage
    """
    rules = None
    rule = None

    def dispatch(self, request, **kwargs):
        """Entrypoint for view

        1. Select rule from rules.
        2. Decorate view
        3. Call `validate` method.
        
        Args:
            - request (Request): Request object.
            - \**kwargs: kwargs from urls.py.

        Returns:
            HttpResponse: django http response
        """
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

        return base(request, **kwargs)

    # validator
    def validate(self, request, **kwargs):
        """
        1. Call `request_valid` method if validation is successfull or missed.
        2. Call `request_invalid` method otherwise.
        
        Args:
            - request (Request): Request object
            - \**kwargs: kwargs from urls.py.

        Returns:
            - HttpResponse: django http response
        """
        # data
        data = request.GET if self.request.method == 'get' else request.POST

        # no validator
        if not self.rule.validator:
            return self.request_valid(data, **kwargs)

        # validate
        validator = self.rule.validator(**self.get_validator_kwargs(data))
        if validator.is_valid():
            return self.request_valid(validator.cleaned_data, **kwargs)
        else:
            return self.request_invalid(validator)

    # error_serializer
    def request_invalid(self, validator):
        """Return result of error_serializer
        
        Args:
            - validator: validator object with `errors` attr.

        Returns:
            - HttpResponse: django http response
        """
        return self.rule.error_serializer(
            request=self.request,
            validator=validator,
        )

    # controller
    def request_valid(self, data, **kwargs):
        """Call controller.

        Get response from controller and return result of validate_response
        method.
        
        Args:
            - data: cleaned and validated data from user.
            - \**kwargs: kwargs from urls.py.

        Returns:
            - HttpResponse: django http response
        """
        # get response from controller
        response = self.rule.controller(self.request, data, **kwargs)
        return self.validate_response(response)

    # post_validator
    def validate_response(self, response):
        """Validate response by post-validator

        1. Return make_response method result if post_validator is missed.
        2. Validate data by post_validator otherwise and call
            response_valid if validation is passed
            or response_invalid otherwise.
        
        Args:
            - response: data from controller

        Returns:
            - HttpResponse: django http response
        """
        # no post-validator
        if not self.rule.post_validator:
            return self.make_response(data=response)

        # post-validation
        params = self.get_validator_kwargs(response)
        validator = self.rule.post_validator(**params)
        if validator.is_valid():
            return self.response_valid(validator)
        else:
            return self.response_invalid(validator)

    # bad response
    def response_invalid(self, validator):
        """Return result of response_error_serializer.
        
        Args:
            - validator: post_validator object with `errors` attr.

        Returns:
            - HttpResponse: django http response
        """
        return self.rule.response_error_serializer(
            request=self.request,
            validator=validator,
        )

    # response
    def response_valid(self, validator):
        """Return result of make_response.
        
        Args:
            - validator: validator object with `cleaned_data` attr.

        Returns:
            - HttpResponse: django http response
        """
        return self.make_response(validator.cleaned_data)

    def make_response(self, data):
        """Make response by serializer
        
        Args:
            - data: validated and cleaned data from controller

        Returns:
            - HttpResponse: django http response
        """
        return self.rule.serializer(request=self.request, data=data)

    # send request and data into validator
    def get_validator_kwargs(self, data):
        """Get kwargs for validators
        
        Args:
            - data: source data from user.

        Returns:
            - dict: kwargs for (post)validator
        """
        kwargs = super(ViewBase, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['data'] = data
        return kwargs
