from rest_framework.throttling import SimpleRateThrottle, AnonRateThrottle

class AuthenticatedUserThrottle(SimpleRateThrottle):
    scope = 'authenticated_user'
    THROTTLE_RATES = {
        'authenticated_user': '100/day',
    }

    def get_cache_key(self, request, view):
        user = request.user
        if user and user.is_authenticated:
            return self.get_ident(request) + str(user.pk)
        return None

class AnonymousUserThrottle(AnonRateThrottle):
    scope = 'anon'
    THROTTLE_RATES = {
        'anon': '20/day',
    }

    def get_cache_key(self, request, view):
        return self.get_ident(request)



