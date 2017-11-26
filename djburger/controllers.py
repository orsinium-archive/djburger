# -*- coding: utf-8 -*-
# django
from django.shortcuts import get_object_or_404
from django.views.generic import ListView


__all__ = ['List', 'Info', 'Add', 'Edit', 'Delete', 'ViewAsController']


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
