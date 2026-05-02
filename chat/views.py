from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Channel, Message

User = get_user_model()

@login_required
def index(request):
    # Pobieramy wszystkie publiczne kanały tekstowe
    text_channels = Channel.objects.filter(channel_type='text', is_public=True)
    voice_channels = Channel.objects.filter(channel_type='voice', is_public=True)
    
    return render(request, 'chat/index.html', {
        'text_channels': text_channels,
        'voice_channels': voice_channels,
    })

@login_required
def channel_view(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id)
    
    blocked_ids = list(request.user.blocked_users.values_list('id', flat=True))

    chat_messages = Message.objects.filter(
        channel=channel,
        is_deleted=False
    ).select_related('author').order_by('created_at')[:50]

    text_channels = Channel.objects.filter(channel_type='text', is_public=True)
    voice_channels = Channel.objects.filter(channel_type='voice', is_public=True)

    is_moderator = request.user.is_staff or request.user.groups.filter(
        name__in=['Administrator', 'Moderator']
    ).exists()
    
    return render(request, 'chat/channel.html', {
        'channel': channel,
        'chat_messages': chat_messages,
        'text_channels': text_channels,
        'voice_channels': voice_channels,
        'is_moderator': is_moderator,
        'blocked_ids': blocked_ids,
    })

@login_required
def dm_view(request, username):
    other_user = get_object_or_404(User, username=username)
    
    # Sprawdzamy czy któryś z użytkowników zablokował drugiego
    if other_user in request.user.blocked_users.all():
        return render(request, 'chat/dm_blocked.html', {'other_user': other_user, 'reason': 'Zablokowałeś tego użytkownika.'})
    
    if request.user in other_user.blocked_users.all():
        return render(request, 'chat/dm_blocked.html', {'other_user': other_user, 'reason': 'Ten użytkownik Cię zablokował.'})
    
    chat_messages = Message.objects.filter(
        Q(author=request.user, dm_recipient=other_user) |
        Q(author=other_user, dm_recipient=request.user),
        is_deleted=False
    ).order_by('created_at')[:50]
    
    users = User.objects.exclude(id=request.user.id)
    
    return render(request, 'chat/dm.html', {
        'other_user': other_user,
        'chat_messages': chat_messages,
        'users': users,
    })

@login_required
def create_channel(request):
    # Tylko admin i moderator mogą tworzyć kanały
    if not (request.user.is_staff or request.user.groups.filter(name__in=['Administrator', 'Moderator']).exists()):
        return redirect('chat:index')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        channel_type = request.POST.get('channel_type', 'text')
        
        if name:
            channel = Channel.objects.create(
                name=name,
                description=description,
                channel_type=channel_type,
                created_by=request.user,
                is_public=True
            )
            return redirect('chat:channel', channel_id=channel.id)
    
    return redirect('chat:index')

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Autor może usunąć swoją wiadomość, moderator/admin każdą
    can_delete = (
        message.author == request.user or
        request.user.is_staff or
        request.user.groups.filter(name__in=['Administrator', 'Moderator']).exists()
    )
    
    if can_delete and request.method == 'POST':
        message.is_deleted = True
        message.save()
    
    if message.channel:
        return redirect('chat:channel', channel_id=message.channel.id)
    return redirect('chat:index')

@login_required
def users_list(request):
    query = request.GET.get('q', '')
    users = User.objects.exclude(id=request.user.id)
    if query:
        users = users.filter(username__icontains=query)
    return render(request, 'chat/users_list.html', {'users': users, 'query': query})

@login_required
def toggle_reaction(request, message_id):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        emoji = data.get('emoji', '')
        
        message = get_object_or_404(Message, id=message_id)
        from .models import Reaction
        
        # Jeśli reakcja istnieje — usuń, jeśli nie — dodaj
        reaction, created = Reaction.objects.get_or_create(
            message=message,
            user=request.user,
            emoji=emoji
        )
        if not created:
            reaction.delete()
            action = 'removed'
        else:
            action = 'added'
        
        # Zliczamy wszystkie reakcje dla tej wiadomości
        reactions = {}
        for r in Reaction.objects.filter(message=message):
            reactions[r.emoji] = reactions.get(r.emoji, 0) + 1
        
        from django.http import JsonResponse
        return JsonResponse({'action': action, 'reactions': reactions})
    
    from django.http import JsonResponse
    return JsonResponse({'error': 'Method not allowed'}, status=405)