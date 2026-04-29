from django.db import models
from django.conf import settings

class Channel(models.Model):
    CHANNEL_TYPES = [
        ('text', 'Tekstowy'),
        ('voice', 'Głosowy'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Typ kanału - tekstowy lub głosowy
    channel_type = models.CharField(max_length=10, choices=CHANNEL_TYPES, default='text')
    
    # Publiczny = widoczny dla wszystkich, prywatny = tylko zaproszeni
    is_public = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_channels'
    )
    
    # Członkowie kanału
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='channels', blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.name}"


class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Tekst'),
        ('image', 'Obraz'),
        ('audio', 'Audio'),
    ]
    
    # Wiadomość może być albo na kanale albo DM - jedno z dwóch
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE,
        related_name='messages', null=True, blank=True
    )
    
    # Odbiorca DM (wiadomości prywatnej)
    dm_recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='received_dms'
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='messages'
    )
    
    content = models.TextField(blank=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    
    # Plik - obrazek lub nagranie audio
    file = models.FileField(upload_to='messages/', null=True, blank=True)
    
    # Usunięta wiadomość - nie kasujemy z bazy, tylko oznaczamy
    is_deleted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} [{self.created_at:%Y-%m-%d %H:%M}]"


class Reaction(models.Model):
    # Reakcja emoji na wiadomość
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10)

    class Meta:
        # Jeden użytkownik może dodać daną reakcję tylko raz na daną wiadomość
        unique_together = ('message', 'user', 'emoji')

    def __str__(self):
        return f"{self.user} {self.emoji} na {self.message.id}"