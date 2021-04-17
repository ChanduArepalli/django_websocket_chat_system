
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from channels.auth import AuthMiddlewareStack
from django.conf.urls import url
from django.urls import path

from chat.consumer import ChatConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path('messsages/<username>/', ChatConsumer.as_asgi()),
                ]
            )
        )
    )
})
