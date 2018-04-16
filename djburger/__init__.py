"""
DjBurger.
framework for big Django projects.

* Split Django views into steps for secure and clean code.
* Provide built-in objects for all steps.
* Integrates this many side libraries like Django REST Framework.
* Django independent.
"""

# main package info
__title__ = 'DjBurger'
__version__ = '0.9.0'
__author__ = 'Gram Orsinium'
__license__ = 'LGPL 3.0'


# version synonym
VERSION = __version__

# built-in
from functools import partial       # noQA


# project
from . import controllers   # noQA
from . import exceptions    # noQA
from . import parsers       # noQA
from . import renderers     # noQA
from . import validators    # noQA

from .views import rule, ViewBase    # noQA


from .utils import is_django_active  # noQA
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
