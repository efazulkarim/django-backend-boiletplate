"""Core app URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_check, name='health-check'),
    path('ready/', views.readiness_check, name='readiness-check'),
]
