# django
from django.shortcuts import get_object_or_404
from django.views.generic import ListView


__all__ = [
    'ListController', 'InfoController',
    'AddController', 'EditController', 'DeleteController',
]


class ListController(ListView):

    def __init__(self, only_data=True, **kwargs):
        self.only_data = only_data
        super(ListController, self).__init__(**kwargs)

    def __call__(request, data, **kwargs):
        self.data = data
        return self.get(self, request, *args, **kwargs)

    def get_queryset(self):
        q = super(ListController, self).get_queryset()
        return q.filter(**self.data)
    
    def get_context_data(self, **kwargs):
        context = super(ListController, self).get_context_data(**kwargs)
        # возвращаем только список объектов
        if self.only_data:
            return context['object_list']
        return context

    def render_to_response(self, context, **response_kwargs):
        return context


class InfoController(object):

    def __init__(self, queryset):
        self.q = queryset

    def __call__(request, data, **kwargs):
        return get_object_or_404(q, **kwargs)


class AddController(object):

    def __init__(self, model):
        self.model = model

    def __call__(request, data, **kwargs):
        return self.model._default_manager.create(**data)


class EditController(object):

    def __init__(self, model, filters=None):
        self.model = model

    def __call__(request, data, **kwargs):
        obj = get_object_or_404(self.model, **kwargs)
        obj.__dict__.update(data)
        return obj.save(force_update=True)


class DeleteController(object):

    def __init__(self, model, filters=None):
        self.model = model

    def __call__(request, data, **kwargs):
        obj = get_object_or_404(self.model, **kwargs)
        return obj.delete()
