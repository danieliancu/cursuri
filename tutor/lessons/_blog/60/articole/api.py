from rest_framework import permissions, viewsets

from .models import Articol
from .serializers import ArticolSerializer


class EsteAutorulSauDoarCitire(permissions.BasePermission):
    """Oricine poate citi; doar autorul poate modifica sau șterge un articol."""

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.autor == request.user


class ArticolViewSet(viewsets.ModelViewSet):
    queryset = Articol.objects.filter(publicat=True).select_related("categorie", "autor")
    serializer_class = ArticolSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, EsteAutorulSauDoarCitire]

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)
