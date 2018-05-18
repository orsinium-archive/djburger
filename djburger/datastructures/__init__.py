# project
from ..utils import is_django_installed

# Django
if is_django_installed:
    from django.http.request import QueryDict, MultiValueDict as MultiDict
else:
    from .querydict import QueryDict  # noQA
    from .multidict import MultiDict  # noQA
