"""API views for example endpoints."""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['GET'])
def api_root(request):
    """API root endpoint."""
    return Response({
        'message': 'Welcome to My API Project',
        'version': '0.1.0',
        'endpoints': {
            'health': '/health/',
            'ready': '/health/ready/',
            'auth': '/api/auth/',
        },
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_profile(request):
    """Get current user profile."""
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    return Response({
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'is_staff': request.user.is_staff,
    }, status=status.HTTP_200_OK)
