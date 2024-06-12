from rest_framework import permissions, viewsets

from .models import UserInfo
from .serializers import (UserSerializerForDB, UserSerializerForResponse)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UserInfo.objects.all().order_by('time')
    serializer_class = UserSerializerForResponse
    permission_classes = [permissions.IsAuthenticated]
