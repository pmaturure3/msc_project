from django.urls import re_path as url
from django.urls import path, include
from app01_phish_detector import views 
urlpatterns = [
    path('', views.index, name='index'),
]