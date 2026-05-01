from django.urls import path
from . import views

app_name = 'voice'

urlpatterns = [
    path('room/<int:channel_id>/', views.voice_room, name='room'),
]