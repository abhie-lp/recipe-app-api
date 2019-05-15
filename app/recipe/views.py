from .serializers import TagSerializer
from core.models import Tag

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage tags in the database"""

    serializer_class = TagSerializer
    authentication_classes = TokenAuthentication,
    permission_classes = IsAuthenticated,
    queryset = Tag.objects.all()

    def get_queryset(self):

        return self.queryset.filter(user=self.request.user).order_by("-name")
