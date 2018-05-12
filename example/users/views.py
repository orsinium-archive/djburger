# external
import djburger
# django
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_exempt as _csrf_exempt
# app
from . import controllers
from . import validators


class AuthAPIView(djburger.ViewBase):
    csrf_exempt = True
    default_rule = djburger.rule(
        prevalidator=AuthenticationForm,
        controller=controllers.UserController.auth,
        postvalidator=djburger.v.c.IsBool,
        renderer=djburger.r.JSON(),
    )


class GroupCommonAPIView(djburger.ViewBase):
    csrf_exempt = True
    rules = {
        'get': djburger.rule(
            controller=controllers.GroupController.list,
            postvalidator=djburger.v.c.QuerySet,
            renderer=djburger.r.JSON(),
        ),
        'post': djburger.rule(
            prevalidator=validators.GroupInputValidator,
            controller=controllers.GroupController.add,
            postvalidator=djburger.v.c.ModelInstance,
            renderer=djburger.r.JSON(),
        ),
        'put': 'post',
    }


class GroupActionsAPIView(djburger.ViewBase):
    csrf_exempt = True
    rules = {
        'get': djburger.rule(
            controller=controllers.GroupController.info,
            postvalidator=djburger.v.c.ModelInstance,
            renderer=djburger.r.JSON(),
        ),
        'patch': djburger.rule(
            prevalidator=validators.GroupInputValidator,
            controller=controllers.GroupController.edit,
            postvalidator=djburger.v.c.ModelInstance,
            renderer=djburger.r.JSON(),
        ),
        'post': 'patch',
        'delete': djburger.rule(
            controller=controllers.GroupController.delete,
            postvalidator=djburger.v.c.IsInt,
            renderer=djburger.r.JSON(),
        ),
    }
