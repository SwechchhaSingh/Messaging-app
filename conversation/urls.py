from django.conf.urls import patterns, url
from django.views import generic
from conversation import views

urlpatterns = patterns('',
    url(r'^$', 'conversation.views.index', name='index'),
    url(r'^login/$', 'conversation.views.login_user', name ='login'),
    url(r'^logout/$', 'conversation.views.logout_user', name='logout'),
    url(r'^home/$', 'conversation.views.home', name='home'),
    url(r'^signup/$', 'conversation.views.signup', name='signup'),
    url(r'^new_message/$', 'conversation.views.new_message', name='new_message'),
    url(r'^view_message/(?P<message_id>\d+)/$', 'conversation.views.view_message', name='view_message'),
    url(r'^list_message/$', 'conversation.views.list_message', name='list_message'),
)

