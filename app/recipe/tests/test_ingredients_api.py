from ..serializers import IngredientSerializer
from core.models import Ingredient, Recipe

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient


INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientAPITest(TestCase):
    """Test the publicaly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_always_required(self):
        """Test that login is required to access the endpoint"""

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test private ingredients API"""

    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="test@django.com",
            password="django123",
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_test(self):
        """Test retrieving a list of ingredients"""

        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Salt")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_logged_in_user(self):
        """Test that ingredients returned for only logged-in user"""

        user2 = get_user_model().objects.create_user(
            email="test2@django.com",
            password="django123",
        )

        Ingredient.objects.create(user=user2, name="Kale")
        ingredient = Ingredient.objects.create(user=self.user, name="Salt")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)

    def test_create_ingredient_successfull(self):
        """Test that creating a new ingredient is success"""

        payload = {"name": "Cabbage"}

        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload["name"]
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient failed"""
        payload = {"name": ""}

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering recipes that are assigned to recipes"""

        ingredient1 = Ingredient.objects.create(user=self.user, name="Banana")
        ingredient2 = Ingredient.objects.create(user=self.user, name="Mango")
        recipe = Recipe.objects.create(
            title="Banana Shake",
            time_minutes=10,
            price=40.00,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
