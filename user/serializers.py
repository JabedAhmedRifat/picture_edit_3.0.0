from rest_framework import serializers

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password':{'write_only':True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
            )
        return user 
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        

class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError({"message":"wrong information"})
    
    
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    
    
    
    
# api__key 

from knox.models import AuthToken
from rest_framework import serializers
from .models import APIKey

class APIKeySerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='auth_token.key', read_only=True)

    class Meta:
        model = APIKey
        fields = ('user', 'auth_token', 'key', 'created_at')