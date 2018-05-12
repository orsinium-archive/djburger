from django.contrib.auth import get_user_model, login
from django.contrib.auth.models import Group

import djburger


UserModel = get_user_model()


class UserController:

    @classmethod
    def auth(cls, request, data):
        user = UserModel._default_manager.get_by_natural_key(data['username'])
        login(request, user)
        return True


class GroupController:
    list = staticmethod(djburger.controllers.List(model=Group))
    info = staticmethod(djburger.controllers.Info(model=Group))
    add = staticmethod(djburger.controllers.Add(model=Group))
    edit = staticmethod(djburger.controllers.Edit(model=Group))
    delete = staticmethod(djburger.controllers.Delete(model=Group))
