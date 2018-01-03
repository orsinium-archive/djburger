# built-in
from functools import partial       # noQA


# project
from . import controllers
from . import exceptions
from . import parsers
from . import renderers
from . import validators

from .views import rule, ViewBase    # noQA


from .utils import is_django_active
# django
if is_django_active:
    from django import forms
    f = forms


# shortcuts
c = controllers
e = exceptions
p = parsers
r = renderers
v = validators


# aliases
View = BaseView = ViewBase
