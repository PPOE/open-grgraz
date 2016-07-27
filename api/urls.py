from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^groups/$', views.groups, name='groups'),
    url(r'^groups/(?P<id>[\d\w]+)/$', views.group_detail, name='group_detail'),
]
