from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^groups/$', views.groups, name='groups'),
    url(r'^groups/(?P<id>[\d\w]+)/$', views.group_detail, name='group_detail'),
    url(r'^sessions/$', views.parliamentary_sessions, name='sessions'),
    url(r'^persons/$', views.council_persons, name='persons'),
    url(r'^types/$', views.motion_types, name='types'),
    url(r'^files/$', views.files, name='files'),
    url(r'^motions/$', views.motions, name='motions'),
]
