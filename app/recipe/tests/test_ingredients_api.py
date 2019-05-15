from ..serializers import IngredientSerializer
from core.models import Ingredient

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