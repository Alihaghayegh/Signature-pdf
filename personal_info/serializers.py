from rest_framework import serializers
from .models import UserInfo
from django.contrib.auth.models import User

class UserSerializerForDB(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['username', 'password', 'first_name', 'last_name', 'signature']

    def create(self, validated_data):
        user = UserInfo.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            signature=validated_data['signature']
        )
        return user

class UserSerializerForResponse(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['username', 'first_name', 'last_name', 'signature']
