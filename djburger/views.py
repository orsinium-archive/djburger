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


_fields = ('decorators', 'parser', 'prevalidator', 'prerenderer', 'controller',
           'postvalidator', 'postrenderer', 'renderer')
_aliases = ('d', 'p', 'prev', 'prer', 'c', 'postv', 'postr', 'r')
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
        ...     decorators=[login_required, csrf_exempt],
        ...     prevalidator=SomeDjangoForm,
        ...     prerenderer='postrenderer',
        ...     # ^ here `prerenderer` point to `postrenderer`
        ...     controller=some_controller,
        ...     postvalidator=None,
        ...     # ^ here post-validator is missed
        ...     postrenderer='renderer',
        ...     renderer=djburger.renderers.JSON(),
        ... )

    :param list decorators: list of decorators.
    :param callable parser: parse request body. `djburger.parsers.Default` by default.
    :param djburger.validators.bases.IValidator prevalidator: validate and clean user params.
    :param callable prerenderer: renderer for pre-validation errors.
    :param callable controller:
    :param djburger.validators.bases.IValidator postvalidator: validate and clean response.
    :param callable postrenderer: renderer for post-validation errors.
    :param callable renderer: renderer for successfull response.

    :return: rule.
    :rtype: djburger._Rule

    :raises TypeError: if missed `c` or `r`.
    """
    # aliases support
    for field, alias in zip(_fields, _aliases):
        if alias in kwargs:
            kwargs[field] = kwargs[alias]

    # check required kwargs
    if 'controller' not in kwargs:
        TypeError('Controller is required')
    if 'renderer' not in kwargs:
        TypeError('Renderer is required')
    # set default parser
    if 'parser' not in kwargs:
        kwargs['parser'] = _DefaultParser()
    # set 'r' as default for error-renderers
    for field in ('prerenderer', 'postrenderer'):
        if field not in kwargs:
            kwargs[field] = 'renderer'
    # set None as default for others
    for field in ('decorators', 'prevalidator', 'postvalidator'):
        if field not in kwargs:
            kwargs[field] = None

    # crosslinks support
    for k, v in kwargs.items():
        kwargs[k] = _get_value(v, kwargs)

    # drop aliases and junk
    kwargs = {field: kwargs[field] for field in _fields}
    # make namedtuple
    return _Rule(**kwargs)


class ViewBase(View):
    """Base views for DjBurger usage.

    :param django.http.request.HttpRequest request: user request object.
    :param \**kwargs: kwargs from urls.py.

    :return: django response.
    :rtype: django.http.HttpResponse
    """
    rules = None
    rule = None
    default_rule = None

    @classonlymethod
    def as_view(cls, **initkwargs):  # noQA
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
        if self.rule.decorators:
            for decorator in self.rule.decorators:
                base = decorator(base)

        return base(request, **kwargs)

    def get_data(self, request):
        """Extract data from request by parser.

        :param django.http.request.HttpRequest request: user request object.

        :return: parsed data.
        """
        return self.rule.parser(request)

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
        if not self.rule.prevalidator:
            return self.request_valid(data, **kwargs)

        # validate
        validator = self.rule.prevalidator(**self.get_validator_kwargs(data))
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

        :param djburger.validators.bases.IValidator validator: validator object with `errors` attr.
        :param int status_code: status code for HTTP-response.

        :return: django response.
        :rtype: django.http.HttpResponse
        """
        return self.rule.prerenderer(
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
            response = self.rule.controller(self.request, data, **kwargs)
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
        if not self.rule.postvalidator:
            return self.make_response(data=response)

        # post-validation
        params = self.get_validator_kwargs(response)
        validator = self.rule.postvalidator(**params)
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

        :param djburger.validators.bases.IValidator validator: validator object with `errors` attr.
        :param int status_code: status code for HTTP-response.

        :return: django response.
        :rtype: django.http.HttpResponse
        """
        return self.response_invalid(validator, status_code)

    # post-validation error renderer
    def response_invalid(self, validator, status_code):
        """Return result of postr (renderer for post-validation errors).

        :param djburger.validators.bases.IValidator validator: validator object with `errors` attr.
        :param int status_code: status code for HTTP-response.

        :return: django response.
        :rtype: django.http.HttpResponse
        """
        return self.rule.postrenderer(
            request=self.request,
            validator=validator,
            status_code=status_code,
        )

    # successfull response renderer
    def response_valid(self, validator):
        """Return result of make_response.
        This method calls only if postv is not None.

        :param djburger.validators.bases.IValidator validator: validator object with `cleaned_data` attr.

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
        return self.rule.renderer(request=self.request, data=data)

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
