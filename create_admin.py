
"""
create_admin.py
---------------
Skrypt inicjalizacyjny aplikacji Discord Clone.
Tworzony automatycznie podczas procesu budowania na serwerze Render.com
z wykorzystaniem bezpłatnego planu hostingowego.

Skrypt wykonuje:
- Utworzenie konta administratora jeśli nie istnieje
- Inicjalizację systemu ról użytkowników (Administrator, Moderator, Użytkownik)
- Przypisanie domyślnych uprawnień do konta administratora

Wywoływany przez build.sh podczas każdego deployu.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@admin.com', 'Admin2026!@#')
    print("Konto administratora zostało utworzone.")
else:
    print("Konto administratora już istnieje.")

for name in ['Administrator', 'Moderator', 'Użytkownik']:
    group, created = Group.objects.get_or_create(name=name)
    print(f"Grupa '{name}': {'utworzona' if created else 'już istnieje'}.")

admin = User.objects.get(username='admin')
admin_group = Group.objects.get(name='Administrator')
admin.groups.add(admin_group)
print("Inicjalizacja zakończona.")