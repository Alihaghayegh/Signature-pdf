import os
from django.http import HttpResponse
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from personal_info.tasks import create_pdf

from .models import UserInfo
from .serializers import UserSerializerForDB, UserSerializerForResponse


@api_view(['GET', 'POST'])
def hello_world(request):
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def users_list(request):
    queryset = UserInfo.objects.all()
    serializer = UserSerializerForResponse(queryset, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_view(request, pk):
    try:
        user_info = UserInfo.objects.get(pk=pk)
    except UserInfo.DoesNotExist:
        return HttpResponse(status=404)
    serializer = UserSerializerForResponse(user_info)
    return Response(serializer.data)


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
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([permissions.AllowAny])
def user_create(request):
    if request.method == 'POST':
        serializer = UserSerializerForDB(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_pdf(request):
    user = request.user
    user_info = UserInfo.objects.get(id=user.id)
    
    if not user_info.signature:
        return Response({"error": "Signature not found"}, status=status.HTTP_400_BAD_REQUEST)
    
    result = create_pdf.delay(user_info.id)
    return Response({"task_id": result.id}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_pdf_status(request, task_id):
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    
    if result.state == 'PENDING':
        return Response({"status": "Pending"}, status=status.HTTP_202_ACCEPTED)
    elif result.state == 'SUCCESS':
        return Response({"status": "Completed", "pdf_url": result.get()}, status=status.HTTP_200_OK)
    else:
        return Response({"status": "Failed"}, status=status.HTTP_400_BAD_REQUEST)
