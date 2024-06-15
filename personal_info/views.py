from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import UserInfo
from .serializers import UserSerializerForDB, UserSerializerForResponse


@api_view(['GET', 'POST'])
def hello_world(request):
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})

@permission_classes[permissions.IsAdminUser, permissions.IsAuthenticated]
@api_view(["GET"])
def users_list(request):
    queryset = UserInfo.objects.all()
    serializer = UserSerializerForResponse(queryset, many=True)
    return Response(serializer.data)

@permission_classes[permissions.IsAdminUser, permissions.IsAuthenticated]
@api_view(["GET"])
def user_view(request, pk):
    try:
        user_info = UserInfo.objects.get(pk=pk)
    except UserInfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializerForResponse(user_info)
    return Response(serializer.data)

@permission_classes[permissions.AllowAny]
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the user'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
            'signature': openapi.Schema(type=openapi.TYPE_FILE, description='Signature file')
        },
        required=['username', 'password',
                  'first_name', 'last_name', 'signature']
    ),
    responses={200: "Success"}
)
@parser_classes([MultiPartParser, FormParser])
@api_view(["POST"])
def user_create(request):
    if request.method == 'POST':
        serializer = UserSerializerForDB(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
