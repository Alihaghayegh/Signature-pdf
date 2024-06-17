from rest_framework import serializers
from .models import UserInfo, PDFFile


class UserSerializerForDB(serializers.ModelSerializer):
    '''
    This serializer is for creating new users
    '''
    class Meta:
        model = UserInfo
        fields = ['username', 'password',
                  'first_name', 'last_name', 'signature']

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
    '''
    This serializer is for returning users in response
    '''
    class Meta:
        model = UserInfo
        fields = ['username', 'first_name', 'last_name', 'signature']


class PDFFileSerializer(serializers.ModelSerializer):
    '''
    This serializer handles serializing pdf in request and response
    '''
    class Meta:
        model = PDFFile
        fields = ['user', 'file', 'status', 'error_message']
