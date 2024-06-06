from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
# from channels.auth import AuthMiddlewareStack
from jwt import decode as jwt_decode
from django.conf import settings

User = get_user_model()

@database_sync_to_async
def get_user(validated_token):
    try:
        user = get_user_model().objects.get(uid=validated_token["user_id"])
        # print("user -->",user)
        return user
    except User.DoesNotExist:
        return AnonymousUser()

class JwtAuthMiddleware(BaseMiddleware):
    
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            token_name, token_key = headers[b'authorization'].decode().split()
            if token_name == 'Bearer':
                decoded_data = jwt_decode(token_key, settings.SECRET_KEY, algorithms=["HS256"])
                scope["user"] =  await get_user(validated_token=decoded_data)
                # print("user ",scope["user"])
        else:
            scope["user"] = AnonymousUser()
        # print("user ---->",scope["user"]==AnonymousUser())
        return await super().__call__(scope, receive, send)

def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(inner)