from django.urls import path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

app_name = 'chat'

# Tymczasowy widok index - zastąpimy go prawdziwym później
@login_required
def temp_index(request):
    return render(request, 'chat/index.html')

urlpatterns = [
    path('', temp_index, name='index'),
]