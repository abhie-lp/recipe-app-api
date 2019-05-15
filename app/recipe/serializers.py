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
        fields = "id", "title", "user", "price", "time_minutes", "tags",\
            "ingredients", "link",
        read_only_fields = "id", "user",
