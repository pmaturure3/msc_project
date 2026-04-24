from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/login/', RedirectView.as_view(url='/oidc/authenticate/', permanent=False)),
    path('admin/', admin.site.urls),
    path('', include('app01_phish_detector.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
]