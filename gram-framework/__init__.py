# built-in
from functools import partial       # noQA

# django
from django import forms            # noQA

# project
import controllers
import serializers
import validators

from views import Rule, ViewBase    # noQA


# shortcuts
f = forms
c = controllers
s = serializers
v = validators
