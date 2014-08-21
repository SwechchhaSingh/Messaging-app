from django.contrib import admin
from conversation.models import MyUser, Message

admin.site.register(MyUser)
admin.site.register(Message)