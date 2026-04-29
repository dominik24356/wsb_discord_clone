from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Avatar - zdjęcie profilowe, zapisywane w media/avatars/
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Bio - krótki opis użytkownika
    bio = models.TextField(max_length=300, blank=True)
    
    # Status online/offline
    is_online = models.BooleanField(default=False)
    
    # Zablokowani użytkownicy - relacja do samego siebie
    # symmetrical=False oznacza: ja blokuję Ciebie, ale Ty nie blokujesz mnie automatycznie
    blocked_users = models.ManyToManyField(
        'self', symmetrical=False, blank=True, related_name='blocked_by'
    )

    def __str__(self):
        return self.username
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default_avatar.png'