from .models import UserInfo
from rest_framework import serializers


class UserSerializerForDB(serializers.ModelSerializer):
    '''
    This class is for getting user info and credetials for saving info database
    '''
    class Meta:
        model = UserInfo
        fields = ['username', 'password', 'first_name', 'last_name', 'signature']



class UserSerializerForResponse(serializers.ModelSerializer):
    '''
    This class is for returning user info and credentials in response
    '''
    class Meta:
        model = UserInfo
        fields = ['first_name', 'last_name', 'signature']