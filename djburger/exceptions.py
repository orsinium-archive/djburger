
# project
from .utils import is_django_installed


# Django
if is_django_installed:
    from django.core.exceptions import ValidationError
else:
    from .mocks import ValidationError


class StatusCodeError(ValidationError):
    """Validation error with specified status code

    Raise it from validator for return validation error with some status code.
    View catch this error and call `prerenderer` or `postrenderer`
    with specified status code.

    :param int status_code: Model for deleting object.
    :param \**kwargs: kwargs for ValidationError.
    """

    def __init__(self, status_code, *args, **kwargs):
        self.status_code = status_code
        super(StatusCodeError, self).__init__(*args, **kwargs)


class SubValidationError(ValidationError):
    """ValidationError for validators in subcontrollers.

    If calidation in subcontroller not passed, subcontroller raise this error
    for stoping execution and returning `postrenderer` with failed
    subcontroller's validator.
    """
    pass


class MultiDictKeyError(KeyError):
    pass


class TooManyFieldsSent(Exception):
    pass
