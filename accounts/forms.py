from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        # Sprawdzamy czy email jest unikalny
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ten email jest już zajęty.")
        return email
    
    def clean_username(self):
        # Sprawdzamy czy login jest unikalny
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ten login jest już zajęty.")
        return username

class LoginForm(AuthenticationForm):
    # Dziedziczymy z gotowego formularza Django, tylko zmieniamy etykiety
    username = forms.CharField(label='Login')
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'bio')
        labels = {
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
            'avatar': 'Zdjęcie profilowe',
            'bio': 'Opis',
        }