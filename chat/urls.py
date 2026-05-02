from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('channel/<int:channel_id>/', views.channel_view, name='channel'),
    path('dm/<str:username>/', views.dm_view, name='dm'),
    path('create-channel/', views.create_channel, name='create_channel'),
    path('delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('users/', views.users_list, name='users_list'),
    path('reaction/<int:message_id>/', views.toggle_reaction, name='toggle_reaction'),
]