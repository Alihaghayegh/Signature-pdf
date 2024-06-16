from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views

urlpatterns = [
    path('user/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/create/', views.user_create, name='user-create'),
    path('users/modify/', views.user_modify, name='user-modify'),
    path('users/', views.users_list, name='users-list'),
    path('users/<int:pk>/', views.user_view, name='user-view'),
    path('api/', include('rest_framework.urls')),
    path('users/generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('users/check_pdf_status/', views.get_task_status, name='check_pdf_status')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
