# -*- coding: utf-8 -*-

# built-in
from collections import namedtuple
# project
from .exceptions import StatusCodeError, SubValidationError
from .parsers import Default as _DefaultParser
from .utils import is_django_installed


# Django
if is_django_installed:
    from django.utils.decorators import classonlymethod
    from django.views.generic import View
else:
    from .mocks import DjangoView as View
    classonlymethod = classmethod


__all__ = ['rule', 'ViewBase']


_fields = ['d', 'p', 'prev', 'c', 'postv', 'prer', 'postr', 'r']
_Rule = namedtuple('Rule', _fields)


def _get_value(v, kwargs):
    if type(v) is str:
        return _get_value(kwargs[v], kwargs)
    else:
        return v


def rule(**kwargs):
    """Factory for _Rule objects

    * Any kwarg can contain str which point where function can get value for kwarg.
    * Some kwargs can contain None.

    Example::
        >>> rule(
        ...     d=[login_required, csrf_exempt],    # decorators
        ...     prev=SomeDjangoForm,    # pre-validator
        ...     c=some_controller,      # controller
        ...     postv=None,             # post-validator
        ...     # ^ here post-validator is missed
        ...     prer='postr',           # renderer for pre-validator errors
        ...     # ^ here `prer` point to `postr`
        ...     postr='r',              # renderer for post-validator errors
        ...     r=djburger.r.JSON(),    # renderer
        ... )

    :param list d: list of decorators.
    :param callable p: parser. Parse request body. `djburger.p.Default` by default.
    :param djburger.v.b.IValidator prev: Validate and clean user params.
    :param callable prer: renderer for pre-validation errors.
    :param callable c: controller.
    :param djburger.v.b.IValidator postv: post-validator. Validate and clean response.
    :param callable postr: renderer for post-validation errors.
    :param callable r: renderer for successfull response.

    :return: rule.
    :rtype: djburger._Rule

    :raises TypeError: if missed `c` or `r`.
    """
    # check required kwargs
    if 'c' not in kwargs:
        TypeError('Controller is required')
    if 'r' not in kwargs:
        TypeError('Renderer is required')
    # set default parser
    if 'p' not in kwargs:
        kwargs['p'] = _DefaultParser()
    # set 'r' as default for error-renderers
    for f in ('prer', 'postr'):
        if f not in kwargs:
            kwargs[f] = 'r'
    # set None as default for others
    for f in ('d', 'prev', 'postv'):
        if f not in kwargs:
            kwargs[f] = None

    for k, v in kwargs.items():
        kwargs[k] = _get_value(v, kwargs)
    return _Rule(**kwargs)


class ViewBase(View):
    """Base views for DjBurger usage

    :param django.http.request.HttpRequest request: user request object.
    :param \**kwargs: kwargs from urls.py.

    :return: django response.
    :rtype: django.http.HttpResponse
    """
    rules = None
    rule = None
    default_rule = None

    @classonlymethod
    def as_view(cls, **initkwargs):
        if not cls.rules and not cls.default_rule:
            raise NotImplementedError('Please, set default_rule or rules attr')
        view = super(ViewBase, cls).as_view(**initkwargs)
        if getattr(cls, 'csrf_exempt', False):
            view.csrf_exempt = cls.csrf_exempt
        return view

    def get_rule(self, method, **kwargs):
        if self.rules and method in self.rules:
            return self.rules[method]
        if self.default_rule:
            return self.default_rule

    def dispatch(self, request, **kwargs):
        """Entrypoint for view

        1. Select rule from rules.
        2. Decorate view
        3. Call `validate` method.

        :param django.http.request.HttpRequest request: user request object.
        :param \**kwargs: kwargs from urls.py.

        :return: django response.
        :rtype: django.http.HttpResponse
        """
        self.method = request.method.lower()
        self.rule = self.get_rule(self.method, **kwargs)
        if self.rule is None:
            # not allowed method
            return self.http_method_not_allowed(request)

        # decorators
        base = self.validate_request
        if self.rule.d:
            for decorator in self.rule.d:
                base = decorator(base)

        return base(request, **kwargs)

    def get_data(self, request):
        """Extract data from request by parser.

        :param django.http.request.HttpRequest request: user request object.

        :return: parsed data.
        """
        return self.rule.p(request)

    # pre-validator
    def validate_request(self, request, **kwargs):
        """
        1. Call `request_valid` method if validation is successfull or missed.
        2. Call `request_invalid` method otherwise.

        :param django.http.request.HttpRequest request: user request object.
        :param \**kwargs: kwargs from urls.py.

        :return: django response.
        :rtype: django.http.HttpResponse
        """
        # data
        data = self.get_data(request)

        # no validator
        if not self.rule.prev:
            return self.request_valid(data, **kwargs)

        # validate
        validator = self.rule.prev(**self.get_validator_kwargs(data))
        try:
            is_valid = validator.is_valid()
        except StatusCodeError as e:
            is_valid = False
            status_code = e.status_code
        else:
            status_code = None
        if is_valid:
            return self.request_valid(validator.cleaned_data, **kwargs)
        else:
            return self.request_invalid(validator, status_code=status_code)

    # pre-validation error renderer
    def request_invalid(self, validator, status_code):
        """Return result of prer (renderer for pre-validator errors)

        :param djburger.v.b.IValidator validator: validator object with `errors` attr.
        :param int status_code: status code for HTTP-response.

        :return: django response.
        :rtype: django.http.HttpResponse
        """
        return self.rule.prer(
            request=self.request,
            validator=validator,
            status_code=status_code,
        )

    # controller
    def request_valid(self, data, **kwargs):
        """Call controller.

        Get response from controller and return result of validate_response
        method.

        :param data: cleaned and validated data from user.
        :param \**kwargs: kwargs from urls.py.

        :return: django response.
        :rtype: django.http.HttpResponse
        """
        # get response from controller
        try:
            response = self.rule.c(self.request, data, **kwargs)
        except SubValidationError as e:
            validator = e.args[0]
            return self.subvalidation_invalid(validator)
        return self.validate_response(response)

    # post-validator
    def validate_response(self, response):
        """Validate response by postv (post-validator)

        1. Return make_response method result if post-validator is missed.
        2. Validate data by post-validator otherwise and call...
            * response_valid if validation is passed
            * or response_invalid otherwise.

        :param response: unvalidated data from controller.

        :return: django response.
        :rtype: django.http.HttpResponse
        """
        # no post-validator
        if not self.rule.postv:
            return self.make_response(data=response)

        # post-validation
        params = self.get_validator_kwargs(response)
        validator = self.rule.postv(**params)
        try:
            is_valid = validator.is_valid()
        except StatusCodeError as e:
            is_valid = False
            status_code = e.status_code
        else:
            status_code = None
        if is_valid:
            return self.response_valid(validator)
        else:
            return self.response_invalid(validator, status_code=status_code)

    # renderer for errors in subcontroller's validator
    def subvalidation_invalid(self, validator, status_code=200):
        """Return result of postr (renderer for post-validation errors).

        :param djburger.v.b.IValidator validator: validator object with `errors` attr.
        :param int status_code: status code for HTTP-response.

        :return: django response.
        :rtype: django.http.HttpResponse
        """
        return self.response_invalid(validator, status_code)

    # post-validation error renderer
    def response_invalid(self, validator, status_code):
        """Return result of postr (renderer for post-validation errors).

        :param djburger.v.b.IValidator validator: validator object with `errors` attr.
        :param int status_code: status code for HTTP-response.

        :return: django response.
        :rtype: django.http.HttpResponse
        """
        return self.rule.postr(
            request=self.request,
            validator=validator,
            status_code=status_code,
        )

    # successfull response renderer
    def response_valid(self, validator):
        """Return result of make_response.
        This method calls only if postv is not None.

        :param djburger.v.b.IValidator validator: validator object with `cleaned_data` attr.

        :return: django response.
        :rtype: django.http.HttpResponse
        """
        return self.make_response(validator.cleaned_data)

    def make_response(self, data):
        """Make response by renderer

        :param data: cleaned and validated data from controller.

        :return: django response.
        :rtype: django.http.HttpResponse
        """
        return self.rule.r(request=self.request, data=data)

    # send request and data into validator
    def get_validator_kwargs(self, data):
        """Get kwargs for validators

        :param data: data which will be validated.

        :return: kwargs for (post)validator.
        :rtype: dict
        """
        try:
            kwargs = super(ViewBase, self).get_form_kwargs()
        except AttributeError:
            kwargs = {}
        kwargs['request'] = self.request
        kwargs['data'] = data
        return kwargs
