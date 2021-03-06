from .. import models
from django.test import TestCase
from django.contrib.auth import get_user_model

from unittest.mock import patch


def sample_user(email="test@django.com", password="django123"):
    """Create a sample user"""

    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):

    def test_create_user_with_successfull(self):
        """Test creating a new user with an email is successfull"""
        email = "test@django.com"
        password = "django123"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        """Test that the email for the new user is normalized"""
        email = "test@DJANGO.com"

        user = get_user_model().objects.create_user(email, "django213")

        self.assertEqual(user.email, email.lower())

    def test_email_field_is_provided(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "django123")

    def test_create_new_super_user(self):
        """Creating a new super user"""
        user = get_user_model().objects.create_superuser(
            email="test@django.com",
            password="dajngo123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """"Test tag's string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="Vegan",
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredients_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Cucumber",
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the recipe model  string representation"""

        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Chhola Bhatura",
            time_minutes=30,
            price=20.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch("uuid.uuid4")
    def test_recipe_filename_uuid(self, mock_uuid):
        """Test that the image is saved in the correct location"""

        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, "myImage.jpg")

        exp_path = f"uploads/recipe/{uuid}.jpg"

        self.assertEqual(file_path, exp_path)
