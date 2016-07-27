from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^groups/$', views.GroupList.as_view(), name='groups'),
    url(r'^groups/(?P<id>[\d\w]+)/$', views.GroupDetail.as_view(), name='group_detail'),
    url(r'^sessions/$', views.SessionList.as_view(), name='sessions'),
    url(r'^persons/$', views.PersonList.as_view(), name='persons'),
    url(r'^types/$', views.TypeList.as_view(), name='types'),
    url(r'^files/$', views.FileList.as_view(), name='files'),
    url(r'^motions/$', views.MotionList.as_view(), name='motions'),
]
