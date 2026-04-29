import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Na razie puste listy - wypełnimy je jak zrobimy consumers
# (consumer = kod obsługujący WebSocket)
websocket_urlpatterns = []

application = ProtocolTypeRouter({
    # Zwykłe requesty HTTP
    "http": get_asgi_application(),
    # WebSockety - real-time chat i głos
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})