"""API views using DRF ViewSets."""
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet

from apps.api.serializers import UserSerializer, UserProfileUpdateSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint."""
    return Response({
        'message': 'Welcome to My API Project',
        'version': '0.1.0',
        'endpoints': {
            'health': '/health/',
            'ready': '/health/ready/',
            'profile': '/api/profile/',
            'auth': '/api/auth/',
        },
    }, status=status.HTTP_200_OK)


class UserViewSet(ViewSet):
    """ViewSet for user-related operations."""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get', 'patch'], url_path='profile')
    def profile(self, request):
        """GET: return current user profile. PATCH: update profile."""
        if request.method == 'PATCH':
            serializer = UserProfileUpdateSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(UserSerializer(request.user).data)

        return Response(UserSerializer(request.user).data)
