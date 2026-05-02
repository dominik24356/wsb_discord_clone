# Discord Clone

Webowa aplikacja komunikacyjna inspirowana platformą Discord, zbudowana w ramach projektu zaliczeniowego.

## Przedmiot
Aplikacje interaktywne w Django

## Opis
Aplikacja umożliwia komunikację użytkowników w czasie rzeczywistym poprzez kanały tekstowe, kanały głosowe oraz wiadomości prywatne. Implementuje system ról i uprawnień, moderację treści oraz rozbudowane funkcje dodatkowe.

## Technologie
- **Backend:** Django 6.0.4, Django Channels, Daphne, Django REST Framework
- **Frontend:** Bootstrap 5, WebRTC, WebSocket API
- **Baza danych:** SQLite (lokalnie), PostgreSQL (produkcja)
- **Real-time:** Django Channels + WebSocket
- **Głos:** WebRTC peer-to-peer
- **Hosting:** Render.com

## Uruchomienie lokalne
```bash
python -m venv dchat_env
dchat_env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
uvicorn core.asgi:application --port 8000 --reload
```

## Funkcjonalności
- Rejestracja, logowanie, edycja profilu
- System ról: Administrator, Moderator, Użytkownik
- Kanały tekstowe i głosowe (WebRTC)
- Wiadomości prywatne (DM)
- Reakcje emoji, powiadomienia, wyszukiwanie
- Moderacja: blokowanie użytkowników, usuwanie wiadomości
- Responsywny interfejs (Bootstrap 5)
