from django.conf.urls import patterns, url
from django.views import generic
from views import *

urlpatterns = patterns('',
    url(r'^$', 'conversation.views.index', name='index'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^home/$', 'conversation.views.home', name='home'),
    url(r'^signup/$', SignupView.as_view(), name='signup'),
    url(r'^new_message/$', 'conversation.views.new_message', name='new_message'),
    url(r'^list_message/view_message/(?P<message_id>\d+)/$', 'conversation.views.view_message', name='view_message'),
    url(r'^list_message/(?P<thread_id>\d+)$', 'conversation.views.list_message', name='list_message'),
    url(r'^list_thread/$', 'conversation.views.list_thread', name='list_thread'),
    url(r'^reply/(?P<thread_id>\d+)$', 'conversation.views.reply', name='reply'),
)

