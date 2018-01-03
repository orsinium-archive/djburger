from django.conf.urls import url
from . import views


urlpatterns = [
    url('auth/?', views.AuthAPIView.as_view(), name='auth'),
    url('group/?', views.GroupCommonAPIView.as_view(), name='auth'),
]
