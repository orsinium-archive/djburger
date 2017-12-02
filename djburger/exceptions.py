
from django.core.exceptions import ValidationError


class StatusCodeError(ValidationError):
    def __init__(self, status_code, msg, **kwargs):
        self.status_code = status_code
        self.msg = msg
        super(StatusCodeError, self).__init__(msg, **kwargs)
