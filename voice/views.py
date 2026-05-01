from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from chat.models import Channel

@login_required
def voice_room(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id, channel_type='voice')
    return render(request, 'voice/room.html', {'channel': channel})