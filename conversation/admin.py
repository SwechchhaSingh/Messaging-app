from django.contrib import admin
from models import MyUser, Thread, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1


class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created_at')
    list_filter = ['created_at']
    search_fields = ['participants']
    fieldsets = [
        ('Participants',            {'fields': ['participants']}),
        ('Thread creation details', {'fields': ('created_at', )}),
    ]
    readonly_fields = ('created_at', )
    inlines = [MessageInline]

    # def get_participants(self, obj):
    #     return "\n".join([p.participants for p in obj.participants.all()])
    # # Thread.objects.get(id=id).participants.all()])


admin.site.register(MyUser)
admin.site.register(Thread, ThreadAdmin)