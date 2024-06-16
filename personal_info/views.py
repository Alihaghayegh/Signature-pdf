import os
from django.http import HttpResponse
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from personal_info.tasks import create_pdf

from .models import UserInfo, PDFFile
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


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_pdf(request):
    user = request.user
    user_info = UserInfo.objects.get(id=user.id)
    
    if PDFFile.objects.filter(user=user_info, status='done').exists():
        pdf_file = PDFFile.objects.get(user=user)
        if pdf_file.status == 'done':
            pdf_file.file.open('rb')
            response = HttpResponse(pdf_file.file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdf_file.file.name}"'
            pdf_file.file.close()
            return response

    if not user_info.signature:
        return Response({"error": "Signature not found"}, status=status.HTTP_400_BAD_REQUEST)
    
    create_pdf.delay(user_info.id)
    return Response({"status": "PDF creation task started"}, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_task_status(request):
    user = request.user
    try:
        pdf_file = PDFFile.objects.get(user=user)
        if pdf_file.status == 'done':
            pdf_file.file.open('rb')
            response = HttpResponse(pdf_file.file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdf_file.file.name}"'
            pdf_file.file.close()
            return response
    except PDFFile.DoesNotExist:
        return Response({"error": "No PDF creation task found for this user."}, status=status.HTTP_404_NOT_FOUND)



    return Response({"status": pdf_file.status, "error_message": pdf_file.error_message})
