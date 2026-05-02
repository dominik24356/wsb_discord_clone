from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from .forms import RegisterForm, LoginForm, EditProfileForm
from .models import User

def register_view(request):
    if request.user.is_authenticated:
        return redirect('chat:index')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Każdy nowy użytkownik dostaje automatycznie grupę "Użytkownik"
            user_group, _ = Group.objects.get_or_create(name='Użytkownik')
            user.groups.add(user_group)
            login(request, user)
            messages.success(request, f'Witaj {user.username}! Konto zostało utworzone.')
            return redirect('chat:index')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('chat:index')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Ustawiamy status online
            user.is_online = True
            user.save()
            login(request, user)
            return redirect('chat:index')
        else:
            messages.error(request, 'Nieprawidłowy login lub hasło.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    # Ustawiamy status offline przed wylogowaniem
    request.user.is_online = False
    request.user.save()
    logout(request)
    return redirect('accounts:login')

@login_required
def profile_view(request, username):
    profile_user = User.objects.get(username=username)
    is_moderator_or_admin = request.user.is_staff or request.user.groups.filter(
        name__in=['Administrator', 'Moderator']
    ).exists()
    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'is_moderator_or_admin': is_moderator_or_admin,
    })

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil zaktualizowany!')
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def block_user(request, username):
    user_to_block = get_object_or_404(User, username=username)
    if request.method == 'POST':
        request.user.blocked_users.add(user_to_block)
    return redirect(request.META.get('HTTP_REFERER', 'chat:users_list'))

@login_required
def unblock_user(request, username):
    user_to_unblock = get_object_or_404(User, username=username)
    if request.method == 'POST':
        request.user.blocked_users.remove(user_to_unblock)
    return redirect(request.META.get('HTTP_REFERER', 'chat:users_list'))