from django.contrib import admin
from django.urls import path
from assignment import views

urlpatterns = [
    path('',views.HomePageView, name='Home_page'),
]
