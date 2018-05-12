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
        postvalidator=djburger.validators.constructors.IsBool,
        renderer=djburger.renderers.JSON(),
    )


class GroupCommonAPIView(djburger.ViewBase):
    csrf_exempt = True
    rules = {
        'get': djburger.rule(
            controller=controllers.GroupController.list,
            postvalidator=djburger.validators.constructors.QuerySet,
            renderer=djburger.renderers.JSON(),
        ),
        'post': djburger.rule(
            prevalidator=validators.GroupInputValidator,
            controller=controllers.GroupController.add,
            postvalidator=djburger.validators.constructors.ModelInstance,
            renderer=djburger.renderers.JSON(),
        ),
        'put': 'post',
    }


class GroupActionsAPIView(djburger.ViewBase):
    csrf_exempt = True
    rules = {
        'get': djburger.rule(
            controller=controllers.GroupController.info,
            postvalidator=djburger.validators.constructors.ModelInstance,
            renderer=djburger.renderers.JSON(),
        ),
        'patch': djburger.rule(
            prevalidator=validators.GroupInputValidator,
            controller=controllers.GroupController.edit,
            postvalidator=djburger.validators.constructors.ModelInstance,
            renderer=djburger.renderers.JSON(),
        ),
        'post': 'patch',
        'delete': djburger.rule(
            controller=controllers.GroupController.delete,
            postvalidator=djburger.validators.constructors.IsInt,
            renderer=djburger.renderers.JSON(),
        ),
    }
