from core.models import Tag, Ingredient, Recipe
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = "id", "name",
        read_only_fields = "id",


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = "id", "name",
        read_only_fields = "id",


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = "id", "title", "price", "time_minutes", "tags",\
            "ingredients", "link",
        read_only_fields = "id", "user",


class RecipeDetailSerializer(RecipeSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer to upload image to recipes"""

    class Meta:
        model = Recipe
        fields = "id", "image",
        read_only_fields = "id",
