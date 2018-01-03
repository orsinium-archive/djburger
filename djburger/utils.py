
try:
    from django.core.exceptions import ImproperlyConfigured
except ImportError:
    is_django_active = False
    is_django_installed = False
else:
    is_django_installed = True
    try:
        from django.conf import settings  # noQA
    except ImproperlyConfigured:
        is_django_active = False
    else:
        is_django_active = True


if is_django_installed:
    from django.db.models import Model
    from django.forms.models import model_to_dict
else:
    Model = dict
    from djburger.mocks import model_to_dict


def safe_model_to_dict(model):
    if not is_django_installed:
        return model
    if isinstance(model, Model):
        return model_to_dict(model)
    return model


class DictInterface(object):
    """Wrapper for adding dict interface to object.

    Useful for models validation with standart validators
    """

    def __init__(self, model):
        self.model = model

    def __getattr__(self, name):
        if name is not 'model':
            return getattr(self.model, name)

    def __setattr__(self, name, value):
        if name is not 'model':
            return setattr(self.model, name, value)

    def __getitem__(self, name):
        return getattr(self.model, name)

    def __setitem__(self, name, value):
        return setattr(self.model, name, value)


def safe_model_dict_interface(model):
    if isinstance(model, Model):
        return DictInterface(model)
    return model
