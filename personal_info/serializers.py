from .models import UserInfo
from rest_framework import serializers


class UserSerializerForDB(serializers.Serializer):
    class Meta:
        model = UserInfo
        fields = ['username', 'password', 'first_name', 'last_name', 'signature', 'time']



class UserSerializerForResponse(serializers.Serializer):
    class Meta:
        model = UserInfo
        fields = ['first_name', 'last_name', 'signature', 'time']