from .models import UserInfo
from rest_framework import serializers


class UserSerializerForDB(serializers.Serializer):
    '''
    This class is for getting user info and credetials for saving info database
    '''
    class Meta:
        model = UserInfo
        fields = ['username', 'password', 'first_name', 'last_name', 'signature', 'time']



class UserSerializerForResponse(serializers.Serializer):
    '''
    This class is for returning user info and credentials in response
    '''
    class Meta:
        model = UserInfo
        fields = ['first_name', 'last_name', 'signature', 'time']