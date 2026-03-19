"""Health check views."""
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def health_check(request):
    """Health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'my-api-project',
        'database': 'connected',
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def readiness_check(request):
    """Readiness check endpoint."""
    return JsonResponse({
        'status': 'ready',
        'service': 'my-api-project',
    }, status=status.HTTP_200_OK)
