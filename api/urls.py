from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^motion/(?P<id>[\d]+)/$', views.motion_detail, name='motion_detail'),
    url(r'^stats/$', views.motion_stats, name='motion_stats'),


    url(r'^api/v0/$', views.api_index, name='api_index'),
    url(r'^api/v0/groups/$', views.ApiGroupList.as_view(), name='groups'),
    url(r'^api/v0/groups/(?P<id>[\d\w]+)/$', views.ApiGroupDetail.as_view(), name='group_detail'),
    url(r'^api/v0/sessions/$', views.ApiSessionList.as_view(), name='sessions'),
    url(r'^api/v0/persons/$', views.ApiPersonList.as_view(), name='persons'),
    url(r'^api/v0/files/$', views.ApiFileList.as_view(), name='files'),
    url(r'^api/v0/motions/$', views.ApiMotionList.as_view(), name='motions'),
    url(r'^api/v0/answers/$', views.ApiAnswerList.as_view(), name='answers'),
]
