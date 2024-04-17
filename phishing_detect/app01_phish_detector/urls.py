from django.urls import re_path as url
from django.urls import path, include
from app01_phish_detector import views 
# from .views import result

urlpatterns = [
    path('', views.index, name='index'),
    path('result/', views.result, name='result'),
    path('about/', views.about, name='about'),

]