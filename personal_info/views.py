import time
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


@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([permissions.IsAuthenticated])
def user_modify(request):
    if request.method == 'PUT':
        user = request.user
        user_info = UserInfo.objects.get(id=user.id)
        pdf_file = PDFFile.objects.get(user=user)
        serializer = UserSerializerForDB(user_info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            pdf_file.status = 'pending'
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Long polling Version
# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def generate_pdf(request):
#     user = request.user
#     user_info = UserInfo.objects.get(id=user.id)

#     pdf_file = PDFFile.objects.filter(user=user_info).first()
#     if pdf_file:
#         if pdf_file.status == 'done':
#             return show_pdf(user)
#         elif pdf_file.status == 'in_progress':
#             return Response({"error": "PDF creation is in progress"}, status=status.HTTP_202_ACCEPTED)
#         elif pdf_file.status == 'failed':
#             create_pdf.delay(user_info.id)
#             return Response({"error": "Previous PDF creation failed. Retrying..."}, status=status.HTTP_202_ACCEPTED)
#     else:
#         if not user_info.signature:
#             return Response({"error": "Signature not found"}, status=status.HTTP_400_BAD_REQUEST)

#         create_pdf_task = create_pdf.delay(user_info.id)
#         create_pdf_task.get()  # Wait for task to complete

#         validate_pdf_task = validate_pdf.delay(user_info.id)
#         is_valid = validate_pdf_task.get()  # Wait for task to complete

#         if is_valid:
#             return show_pdf(user)
#         else:
#             return Response({"error": "PDF creation failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     return HttpResponse(status=404)


# Short polling Version
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_pdf(request):
    user = request.user
    user_info = UserInfo.objects.get(id=user.id)

    pdf_file = PDFFile.objects.filter(user=user_info).first()
    if pdf_file:
        if pdf_file.status == 'done':
            return show_pdf(user)
        elif pdf_file.status == 'in_progress':
            return Response({"error": "PDF creation is in progress"}, status=status.HTTP_202_ACCEPTED)
        elif pdf_file.status == 'failed':
            create_pdf.delay(user_info.id)
            return Response({"error": "Previous PDF creation failed. Retrying..."}, status=status.HTTP_202_ACCEPTED)
    else:
        if not user_info.signature:
            return Response({"error": "Signature not found"}, status=status.HTTP_400_BAD_REQUEST)

        create_pdf.delay(user_info.id)
        for _ in range(5):
            time.sleep(1)
            pdf_file = PDFFile.objects.filter(user=user_info).first()
            if pdf_file.status == 'done':
                # Validate the PDF file
                validate_pdf.delay(user_info.id)
                if pdf_file.status == 'verified':
                    return show_pdf(user)
        return Response({"status": "PDF creation started, please check status later"}, status=status.HTTP_202_ACCEPTED)
