from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chat.urls')),
    path('voice/', include('voice.urls')),
]

# Serwowanie plików media lokalnie (avatary, obrazki, nagrania)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Obsługa błędów
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'