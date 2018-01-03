from django.conf.urls import url
from . import views


urlpatterns = [
    url('auth/?', views.AuthAPIView.as_view(), name='auth'),
    url('groups/?', views.GroupCommonAPIView.as_view(), name='groups'),
    url('group/(?P<pk>\d+)?', views.GroupActionsAPIView.as_view(), name='group'),
]
