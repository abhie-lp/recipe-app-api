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

    def test_create_basic_recipe(self):
        """Test creating recipe"""

        payload = {
            "title": "Sandwich",
            "time_minutes": 10,
            "price": 25.00,
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])

        for key in payload:
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""

        tag1 = sample_tag(user=self.user, name="Lunch")
        tag2 = sample_tag(user=self.user, name="Veg")

        payload = {
            "title": "Chhola Bhatura",
            "tags": [tag1.id, tag2.id],
            "time_minutes": 30,
            "price": 20.00,
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipes with ingredients"""

        ingredient1 = sample_ingredient(user=self.user, name="Ginger")
        ingredient2 = sample_ingredient(user=self.user, name="Tomato")

        payload = {
            "title": "Chhola Bhatura",
            "ingredients": [ingredient1.id, ingredient2.id],
            "time_minutes": 30,
            "price": 20.00,
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_recipe_update(self):
        """Test updating a recipe using PATCH"""

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name="Sweets")

        payload = {
            "title": "Ice cream",
            "tags": [new_tag.id]
        }

        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload["title"])

        tags = recipe.tags.all()

        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating recipe using PUT"""

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            "title": "Chilli Potato",
            "time_minutes": 10,
            "price": 40.00,
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.time_minutes, payload["time_minutes"])
        self.assertEqual(recipe.price, payload["price"])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
