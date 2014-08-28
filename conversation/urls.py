from django.conf.urls import patterns, url
from django.views import generic
from django.contrib.auth.decorators import login_required
from views import *

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^signup/$', SignupView.as_view(), name='signup'),
    url(r'^new_message/$', login_required(NewMessageView.as_view()), name='new_message'),
    url(r'^list_message/view_message/(?P<pk>\d+)/$', login_required(MessageDetailView.as_view()), name='view_message'),
    url(r'^list_message/(?P<pk>\d+)/$', login_required(ListMessageView.as_view()), name='list_message'),
    url(r'^list_thread/$', login_required(ListThreadView.as_view()), name='list_thread'),
    url(r'^reply/(?P<pk>\d+)/$', login_required(ReplyView.as_view()), name='reply'),
)

