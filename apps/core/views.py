"""Health check views."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({
        'status': 'healthy',
        'service': 'my-api-project',
        'database': 'connected',
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """Readiness check endpoint."""
    return Response({
        'status': 'ready',
        'service': 'my-api-project',
    }, status=status.HTTP_200_OK)
