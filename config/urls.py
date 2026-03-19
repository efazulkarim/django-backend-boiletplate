"""URL configuration for My API Project."""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('', include('allauth.urls')),
    path('health/', include('apps.core.urls')),
]
