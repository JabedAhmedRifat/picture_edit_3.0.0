# from functools import wraps
# from knox.auth import TokenAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from .models import APIKey

# def authenticate_with_token_or_api_key(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         # Check for API key in headers
#         api_key = request.headers.get('Authorization')
#         if api_key and api_key.startswith('Api-Key '):
#             api_key_value = api_key.split(' ')[1]
#             try:
#                 api_key_obj = APIKey.objects.get(key=api_key_value)
#                 request.user = api_key_obj.user
#                 return view_func(request, *args, **kwargs)
#             except APIKey.DoesNotExist:
#                 raise AuthenticationFailed('Invalid API key')

#         # If API key not present, fall back to Token authentication
#         token_authentication = TokenAuthentication()
#         user, auth = token_authentication.authenticate(request)
#         if user:
#             request.user = user
#             return view_func(request, *args, **kwargs)

#         # No valid authentication found
#         raise AuthenticationFailed('Invalid authentication method')

#     return _wrapped_view






from functools import wraps
from knox.auth import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import APIKey

def authenticate_with_token_or_api_key(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Try to authenticate with token
        token_authentication = TokenAuthentication()
        user_auth_tuple = token_authentication.authenticate(request)
        
        if user_auth_tuple:
            user, auth = user_auth_tuple
            request.user = user
            return view_func(request, *args, **kwargs)

        # Try to authenticate with API key
        api_key = request.headers.get('Authorization')
        if api_key and api_key.startswith('Api-Key '):
            api_key_value = api_key.split(' ')[1]
            try:
                api_key_obj = APIKey.objects.get(key=api_key_value)
                request.user = api_key_obj.user
                return view_func(request, *args, **kwargs)
            except APIKey.DoesNotExist:
                raise AuthenticationFailed('Invalid API key')

        # No valid authentication found
        request.user = None
        return view_func(request, *args, **kwargs)

    return _wrapped_view