from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
import hashlib
from datetime import datetime, timezone

@database_sync_to_async
def get_user_from_token(token):
    from django.contrib.auth.models import AnonymousUser
    from django.contrib.auth import get_user_model
    from rest_framework_simplejwt.tokens import UntypedToken
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    from rest_framework_simplejwt.authentication import JWTAuthentication
    
    User = get_user_model()
    
    try:
        if not token or len(token) < 10:
            return AnonymousUser()
        
        # Validate JWT token
        UntypedToken(token)
        
        # Get user from token
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
        
        # Security checks
        if not user.is_active or not user.is_email_verified:  # Fixed typo: is_email_varified -> is_email_verified
            return AnonymousUser()
        
        return user
    
    except (InvalidToken, TokenError):
        return AnonymousUser()
    except Exception:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner
        
    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser
        
        token = self.extract_token(scope)
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()
            
        return await self.inner(scope, receive, send)
        
    def extract_token(self, scope):
        # Method1: Query parameters
        query_string = scope.get('query_string', b'').decode()
        if query_string:
            query_params = parse_qs(query_string)
            token = query_params.get('token', [None])[0]
            if token:
                return token
        
        # Method2: Headers
        headers = dict(scope.get('headers', []))
        auth_header = headers.get(b'authorization', b'').decode()
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ', 1)[1]
            
        return None

def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))