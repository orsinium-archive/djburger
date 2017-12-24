# -*- coding: utf-8 -*-
# project
from .exceptions import SubValidationError
from .utils import is_django_installed


# Django
if is_django_installed:
    from django.shortcuts import get_object_or_404
    from django.views.generic import ListView
else:
    from .mocks import DjangoListView as ListView, model_to_dict as get_object_or_404


__all__ = [
    'List', 'Info', 'Add', 'Edit', 'Delete',
    'ViewAsController',
    'pre', 'post', 'subcontroller',
]


class _ModelControllerMixin(object):
    def __init__(self, queryset=None, model=None):
        if queryset:
            self.q = queryset
        elif model:
            self.q = model._default_manager.all()
        else:
            raise ValueError("Queryset or model required.")


class List(ListView):
    """Controller based on Django ListView

    1. Get list of objects
    2. Filter list by validated data from user
    3. Optional pagination

    :param bool only_data: return only filtered queryset if True,
                all context data otherwise. Use `only_data=False` with
                TemplateSerializerFactory.
    :param \**kwargs: all arguments of ListView.

    :return: filtered queryset.
    :rtype: django.db.models.query.QuerySet
    """

    def __init__(self, only_data=True, **kwargs):
        """Initialize controller in rule.
        """
        self.only_data = only_data
        super(List, self).__init__(**kwargs)

    def __call__(self, request, data, **kwargs):
        self.data = data
        return self.get(self, request, **kwargs)

    def get_queryset(self):
        q = super(List, self).get_queryset()
        return q.filter(**self.data)

    def get_context_data(self, **kwargs):
        context = super(List, self).get_context_data(**kwargs)
        # return only filtered queryset
        if self.only_data:
            return context['object_list']
        return context

    def render_to_response(self, context, **response_kwargs):
        return context


class Info(_ModelControllerMixin):
    """Return one object from queryset

    1. Return object filtered by params from URL kwargs  (like `pk` or `slug`)
        if url-pattern have kwargs.
    2. Return object from validated data if data have key `object`
        or data have only one key.
    3. Raise exception otherwise.

    :param django.db.models.query.QuerySet queryset: QuerySet for retrieving object.
    :param django.db.models.Model model: Model for retrieving object.

    :return: one object from queryset or model.
    :rtype: django.db.models.Model

    :raises ValueError: if can't select params for queryset filtering.
    :raises django.http.Http404: if object does not exist or multiple objects returned
    """

    def __call__(self, request, data, **kwargs):
        if kwargs:
            return get_object_or_404(self.q, **kwargs)
        elif 'object' in data:
            return data['object']
        elif len(data) == 1:
            return data.pop()
        else:
            raise ValueError("Can't select object!")


class Add(object):
    """Controller for adding object with validated data.

    :param django.db.models.Model model: Model for adding object.

    :return: created object.
    :rtype: django.db.models.Model
    """

    def __init__(self, model):
        self.model = model

    def __call__(self, request, data, **kwargs):
        return self.model._default_manager.create(**data)


class Edit(_ModelControllerMixin):
    """Controller for editing objects.

    1. Get object of initialized model by URL's kwargs.
    2. Set params from validated data.
    3. Update tuple into database.

    :param django.db.models.query.QuerySet queryset: QuerySet for editing object.
    :param django.db.models.Model model: Model for editing object.

    :return: edited object.
    :rtype: django.db.models.Model

    :raises django.http.Http404: if object does not exist or multiple objects returned
    """

    def __call__(self, request, data, **kwargs):
        obj = get_object_or_404(self.q, **kwargs)
        obj.__dict__.update(data)
        obj.save(force_update=True)
        return obj


class Delete(_ModelControllerMixin):
    """Controller for deleting objects.

    Delete object filtered by URL's kwargs.

    :param django.db.models.query.QuerySet queryset: QuerySet for deleting object.
    :param django.db.models.Model model: Model for deleting object.

    :return: count of deleted objects.
    :rtype: int

    :raises django.http.Http404: if object does not exist or multiple objects returned
    """

    def __call__(self, request, data, **kwargs):
        obj = get_object_or_404(self.q, **kwargs)
        result = obj.delete()
        # hook for old Django versions
        if result is None:
            return 1
        return result[0]


class ViewAsController(object):
    """Allow use any django view as controller.

    1. For CBV with render_to_response method return context.
    2. Return rendered response otherwise.

    :param callable view: view.
    :param str method: optional method which will be forced for request

    :return: if possible response context or content, response object otherwise.
    """

    def __init__(self, view, method=None):
        self.view = self.patch_view(view)
        self.method = method

    @staticmethod
    def patch_view(view):
        """Patch view for getting context instead of rendered response.
        """
        if hasattr(view, 'render_to_response'):
            view.render_to_response = lambda context, **kwargs: context
        return view

    def __call__(self, request, data, **kwargs):
        # set data to request
        method = self.method or request.method
        if method.lower() == 'get':
            request.GET = data
        else:
            request.POST = data

        # get response
        response = self.view(request=request, **kwargs)
        if hasattr(response, 'context'):
            return response.context
        elif hasattr(response, 'content'):
            return response.content
        else:
            return response


class pre(object): # noQA
    """Decorator for input data validation before subcontroller calling

    :param djburger.v.b.IValidator validator: validator for pre-validation.
    :param \**kwargs: kwargs for validator.

    :raises djburger.e.SubValidationError: if pre-validation not passed
    """
    def __init__(self, validator, **kwargs):
        self.validator = validator
        self.validator_kwargs = kwargs

    def __call__(self, controller):
        self.controller = controller
        return self._wrapper

    def _wrapper(self, data, request=None, **kwargs):
        validator = self.validator(
            data=data,
            request=request,
            **self.validator_kwargs
        )
        if not validator.is_valid():
            raise SubValidationError(validator)
        return self.controller(
            data=validator.cleaned_data,
            request=request,
            **kwargs
        )


class post(pre): # noQA
    """Decorator for output data validation before subcontroller calling

    :param djburger.v.b.IValidator validator: validator for post-validation.
    :param \**kwargs: kwargs for validator.

    :raises djburger.e.SubValidationError: if post-validation not passed
    """
    def _wrapper(self, data, request=None, **kwargs):
        result = self.controller(
            data=data,
            request=request,
            **kwargs
        )
        validator = self.validator(
            data=result,
            request=request,
            **self.validator_kwargs
        )
        if not validator.is_valid():
            raise SubValidationError(validator)
        return validator.cleaned_data


def subcontroller(c, prev=None, postv=None):
    """Constructor for subcontrollers
    If any validation failed, immediately raise SubValidationError.

    :param djburger.v.b.IValidator prev: validator for pre-validation.
    :param callable c: controller.
    :param djburger.v.b.IValidator postv: validator for post-validation.

    :raises djburger.e.SubValidationError: if any validation not passed
    """
    if prev:
        c = pre(prev)(c)
    if postv:
        c = post(postv)(c)
    return c
