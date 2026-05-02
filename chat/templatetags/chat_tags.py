from django import template
from chat.models import Channel

register = template.Library()

@register.inclusion_tag('chat/sidebar.html', takes_context=True)
def sidebar(context):
    request = context['request']
    text_channels = Channel.objects.filter(channel_type='text', is_public=True)
    voice_channels = Channel.objects.filter(channel_type='voice', is_public=True)
    can_create = request.user.is_staff or request.user.groups.filter(
        name__in=['Administrator', 'Moderator']
    ).exists()
    return {
        'request': request,
        'text_channels': text_channels,
        'voice_channels': voice_channels,
        'current_channel': context.get('channel', None),
        'can_create': can_create,
    }