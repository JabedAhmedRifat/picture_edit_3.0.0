from knox.auth import TokenAuthentication
from rest_framework import exceptions

class CustomTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        user_auth_tuple = super().authenticate(request)

        if user_auth_tuple is None:
            return None, None  # Return a tuple to avoid unpacking error

        user, auth_token = user_auth_tuple
        if not user:
            raise exceptions.AuthenticationFailed('User not authenticated')

        request.user = user
        return user, auth_token