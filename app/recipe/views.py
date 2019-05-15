from .serializers import TagSerializer, IngredientSerializer
from core.models import Tag, Ingredient

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Manage tags in the database"""

    serializer_class = TagSerializer
    authentication_classes = TokenAuthentication,
    permission_classes = IsAuthenticated,
    queryset = Tag.objects.all()

    def get_queryset(self):

        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, seriializer):
        """Create a new tag"""
        seriializer.save(user=self.request.user)


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    authentication_classes = TokenAuthentication,
    permission_classes = IsAuthenticated,
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

    def get_queryset(self):

        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
