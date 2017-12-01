# built-in
from functools import partial       # noQA

# django
from django import forms

# project
from . import controllers
from . import exceptions
from . import renderers
from . import validators

from .views import rule, ViewBase    # noQA


# shortcuts
c = controllers
e = exceptions
f = forms
r = renderers
v = validators
