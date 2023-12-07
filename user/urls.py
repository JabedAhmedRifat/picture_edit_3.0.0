from django.urls import path
from .views import *
from knox import views as knox_views

urlpatterns = [
    path('register/', RegistrationAPI.as_view()),
    path('login/', LoginAPI.as_view()),
    path('logout/', knox_views.LogoutView.as_view(),name='logout'),
    path('get-user/', UserAPI.as_view()),
    path('change-password/', changePasswordView),
    
     path('generate-api-key/', generate_api_key),
]