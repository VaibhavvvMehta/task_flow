from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Read JWT token from httpOnly cookie; reject blacklisted tokens."""

    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        if access_token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'

        result = super().authenticate(request)

        if result is not None:
            _, validated_token = result
            jti = validated_token.get('jti')
            if jti and cache.get(f'blacklist:jti:{jti}'):
                return None  # token was invalidated at logout

        return result