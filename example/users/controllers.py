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
    list = staticmethod(djburger.c.List(model=Group))
    info = staticmethod(djburger.c.Info(model=Group))
    add = staticmethod(djburger.c.Add(model=Group))
    edit = staticmethod(djburger.c.Edit(model=Group))
    delete = staticmethod(djburger.c.Delete(model=Group))
