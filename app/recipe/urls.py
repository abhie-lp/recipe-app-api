from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = "recipe"

router = DefaultRouter()
router.register("tags", views.TagViewSet)
router.register("ingredients", views.IngredientViewSet)

urlpatterns = [
    path("", include(router.urls))
]
