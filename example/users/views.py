# external
import djburger
# django
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_exempt as _csrf_exempt
# app
from . import controllers


class AuthAPIView(djburger.ViewBase):
    csrf_exempt = True

    default_rule = djburger.rule(
        prev=AuthenticationForm,
        c=controllers.UserController.auth,
        postv=djburger.v.c.IsBool,
        r=djburger.r.JSON(),
    )


class GroupCommonAPIView(djburger.ViewBase):
    rules = {
        'get': djburger.rule(
            c=controllers.GroupController.list,
            postv=djburger.v.c.QuerySet,
            r=djburger.r.JSON(),
        ),
    }


class GroupActionsAPIView(djburger.ViewBase):
    pass
