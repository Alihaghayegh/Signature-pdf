<<<<<<< HEAD
=======
import redis
>>>>>>> dev
from django.http import HttpResponse
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema

<<<<<<< HEAD
from personal_info.tasks import create_pdf

from .models import UserInfo, PDFFile
from .serializers import UserSerializerForDB, UserSerializerForResponse

=======
from .tasks import create_pdf, validate_pdf
from .utils import show_pdf
from .models import UserInfo, PDFFile
from .serializers import UserSerializerForDB, UserSerializerForResponse

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
>>>>>>> dev

@api_view(['GET', 'POST'])
def hello_world(request):
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})

<<<<<<< HEAD

=======
>>>>>>> dev
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def users_list(request):
    queryset = UserInfo.objects.all()
    serializer = UserSerializerForResponse(queryset, many=True)
    return Response(serializer.data)

<<<<<<< HEAD

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_view(request, pk):
    try:
        user_info = UserInfo.objects.get(pk=pk)
    except UserInfo.DoesNotExist:
        return HttpResponse(status=404)
    serializer = UserSerializerForResponse(user_info)
    return Response(serializer.data)

=======
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
>>>>>>> dev

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

<<<<<<< HEAD

=======
>>>>>>> dev
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([permissions.IsAuthenticated])
def user_modify(request):
    if request.method == 'PUT':
<<<<<<< HEAD
        user = request.user
        user_info = UserInfo.objects.get(id=user.id)
        pdf_file = PDFFile.objects.get(user=user)
        serializer = UserSerializerForDB(user_info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            pdf_file.status == 'pending'
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
=======
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
>>>>>>> dev
@permission_classes([permissions.IsAuthenticated])
def generate_pdf(request):
    user = request.user
    user_info = UserInfo.objects.get(id=user.id)
<<<<<<< HEAD
    
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
=======
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

>>>>>>> dev
