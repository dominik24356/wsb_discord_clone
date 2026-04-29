from django.contrib import admin
from .models import Channel, Message, Reaction

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel_type', 'is_public', 'created_by', 'created_at')
    list_filter = ('channel_type', 'is_public')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('author', 'channel', 'message_type', 'is_deleted', 'created_at')
    list_filter = ('message_type', 'is_deleted')

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'emoji')