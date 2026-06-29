"""API URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.api import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('', include(router.urls)),
    path('auth/', include('allauth.urls')),
]
