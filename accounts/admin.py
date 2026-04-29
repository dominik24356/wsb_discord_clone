from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Dodatkowe kolumny widoczne na liście użytkowników
    list_display = ('username', 'email', 'is_online', 'is_staff')
    # Dodajemy nasze pola do formularza edycji użytkownika
    fieldsets = UserAdmin.fieldsets + (
        ('Profil', {'fields': ('avatar', 'bio', 'is_online', 'blocked_users')}),
    )