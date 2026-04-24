from django.urls import re_path as url
from django.urls import path, include
from django.contrib.auth import views as auth_views
from app01_phish_detector import views


urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('result/', views.result, name='result'),
    path('about/', views.about, name='about'),

    # Django authentication
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]