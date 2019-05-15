from ..serializers import RecipeSerializer, RecipeDetailSerializer
from core.models import Recipe, Tag, Ingredient

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """Return recipe detail URL"""

    return reverse("recipe:recipe-detail", args=[recipe_id])


def sample_tag(user, name="Main Course"):
    """Create and return sample  tag"""

    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Tomato"):
    """Create and return sample ingredient"""

    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **kwargs):
    """Create and return a sample recipe"""

    defaults = {
        "title": "Sample Recipe",
        "time_minutes": 20,
        "price": 30.00,
    }
    defaults.update(kwargs)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITest(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="test@django.com",
            password="django123",
        )

        self.client.force_authenticate(self.user)

    def test_retrieving_recipes(self):
        """Test retrieving a list of recipes"""

        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test list contents only by logged user"""

        recipe = sample_recipe(user=self.user)

        user2 = get_user_model().objects.create_user(
            email="test2@django.com",
            password="django123",
        )
        sample_recipe(user=user2, title="Khhastey")

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], recipe.title)

    def test_view_recipe_detail(self):
        """Test the detail of a single recipe"""

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
