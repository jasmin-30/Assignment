from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from assignment import views

urlpatterns = [
    path('', views.homePageView, name='Home_page'),
    path('logout/', views.Logout, name='Logout'),
    path('dashboard/', views.userDashboard, name='User_Dashboard'),
    path('profile/', views.userProfile, name='User_Profile'),
    path('admin/dashboard/', views.adminView, name='Admin'),

    # API Endpoints
    path('add-info/', views.addInfo, name='add-info'),
    path('edit-info/', views.editInfo, name='edit-info'),
    path('delete-info/', views.deleteInfo, name='delete-info'),
    path('edit-user/', views.editUser, name='edit-user'),
    path('delete-user/', views.deleteUser, name='delete-user'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
