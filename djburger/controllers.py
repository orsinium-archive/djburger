# -*- coding: utf-8 -*-
# django
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
# project
from .exceptions import SubValidationError


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
    """

    def __init__(self, only_data=True, **kwargs):
        """Initialize controller in rule.

        Args:
            only_data (bool): return only filtered queryset if True,
                all context data otherwise. Use `only_data=False` with
                TemplateSerializerFactory.
            **kwargs: all arguments of ListView.
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
    """

    def __init__(self, model):
        """Initialize controller with passed model.
        """
        self.model = model

    def __call__(self, request, data, **kwargs):
        return self.model._default_manager.create(**data)


class Edit(_ModelControllerMixin):
    """Controller for editing objects.

    1. Get object of initialized model by URL's kwargs.
    2. Set params from validated data.
    3. Update tuple into database.
    """

    def __call__(self, request, data, **kwargs):
        obj = get_object_or_404(self.q, **kwargs)
        obj.__dict__.update(data)
        obj.save(force_update=True)
        return obj


class Delete(_ModelControllerMixin):
    """Controller for deleting objects.

    Delete object filtered by URL's kwargs.
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
        if hasattr(response, 'content'):
            return response.content
        else:
            return response


class pre(object): # noQA
    """Decorator for input data validation before subcontroller calling
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
            **self.validator_kwargs,
        )
        if not validator.is_valid():
            raise SubValidationError(validator)
        return self.controller(
            data=validator.cleaned_data,
            request=request,
            **kwargs,
        )


class post(pre): # noQA
    """Decorator for output data validation before subcontroller calling
    """
    def _wrapper(self, data, request=None, **kwargs):
        result = self.controller(
            data=data,
            request=request,
            **kwargs,
        )
        validator = self.validator(
            data=result,
            request=request,
            **self.validator_kwargs,
        )
        if not validator.is_valid():
            raise SubValidationError(validator)
        return validator.cleaned_data


def subcontroller(c, prev=None, postv=None):
    """Constructor for subcontrollers
    If any validation failed, immediately raise SubValidationError.

    Kwargs:
        - prev (callable): validator
        - c (callable): controller
        - postv (callable): post-validator
    """
    if prev:
        c = pre(prev)(c)
    if postv:
        c = post(postv)(c)
    return c
