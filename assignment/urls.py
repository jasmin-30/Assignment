from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from assignment import views


urlpatterns = [
    path('', views.homePageView, name='Home_page'),
    path('logout/', views.Logout, name='Logout'),
    path('dashboard/', views.userDashboard, name='User_Dashboard'),
    path('profile/', views.userProfile, name='User_Profile'),
    path('admin/dashboard/', views.adminView, name='Admin'),

    # API Endpoints
    path('api/info-api/', views.InfoApiView.as_view(), name='info-api'),
    path('api/edit-info/<int:id>/', views.EditInfoApiView.as_view(), name='edit-info-api'),
    # path('edit-user/', views.editUser, name='edit-user'),
    path('api/edit-user/<int:id>/', views.UserApiView.as_view(), name='user-api'),
    path('api/delete-users/', views.DeleteUsers.as_view(), name='delete-user-api'),
    # path('delete-user/', views.deleteUser, name='delete-user'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
