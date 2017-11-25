# built-in
from functools import partial       # noQA

# django
from django import forms

# project
from . import controllers
from . import renderers
from . import validators

from .views import rule, ViewBase    # noQA


# shortcuts
f = forms
c = controllers
r = renderers
v = validators
