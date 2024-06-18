import os
import redis
import time
from io import BytesIO
from django.http import HttpResponse
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema

from .tasks import create_pdf, validate_pdf
from .utils import show_pdf
from .models import UserInfo, PDFFile
from .serializers import UserSerializerForDB, UserSerializerForResponse

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

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
def user_view(request):
    try:
        user = request.user
        user_info = UserInfo.objects.get(id=user.id)
        serializer = UserSerializerForResponse(user_info)
        return Response(serializer.data)
    except UserInfo.DoesNotExist:
        return HttpResponse(status=404)

@swagger_auto_schema(
    method='post',
    required=['username', 'password', 'first_name', 'last_name', 'signature'],
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

@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([permissions.IsAuthenticated])
def user_modify(request):
    if request.method == 'PUT':
        try:
            user = request.user
            user_info = UserInfo.objects.get(id=user.id)
            pdf_file = PDFFile.objects.get(user=user_info)

            # Only update profile picture and PDF status
            data = {'signature': request.data.get('signature')}
            serializer = UserSerializerForDB(user_info, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                redis_client.set(f'pdf_status_{user.id}', 'pending')
                pdf_file.status = 'pending'
                pdf_file.save()  # Saving the pdf_file with updated status
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserInfo.DoesNotExist:
            return HttpResponse(status=404)
        except PDFFile.DoesNotExist:
            return HttpResponse(status=404)

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_pdf(request):
    user = request.user
    user_info = UserInfo.objects.get(id=user.id)
    pdf_status = redis_client.get(f'pdf_status_{user.id}')

    if request.method == 'POST':
        if pdf_status:
            pdf_status = pdf_status.decode('utf-8')
            if pdf_status == 'verified':
                return show_pdf(user)
            elif pdf_status == 'in_progress':
                return Response({"status": "PDF creation in progress"}, status=202)
            elif pdf_status == 'failed':
                create_pdf.delay(user_info.id)
                return Response({"status": "PDF recreation started due to previous failure"}, status=202)

        if not user_info.signature:
            return Response({"error": "Signature not found"}, status=400)

        create_pdf.delay(user_info.id)
        return Response({"status": "PDF creation started"}, status=202)

    elif request.method == 'GET':
        if pdf_status:
            pdf_status = pdf_status.decode('utf-8')
            if pdf_status == 'verified':
                response = show_pdf(user)
                if response:
                    return response
                else:
                    return Response({"error": "PDF not ready"}, status=400)
            elif pdf_status == 'failed':
                # create_pdf.delay(user_info.id)
                create_pdf.apply_async((user_info.id,))
                return Response({"error": "PDF creation or validation failed"}, status=400)
            return Response({"status": pdf_status}, status=200)
        return Response({"status": "not found"}, status=404)

