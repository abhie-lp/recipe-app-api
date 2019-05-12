from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")


# Helper function to create a user
def create_user(**kwargs):
    user = get_user_model().objects.create_user(**kwargs)
    return user


class PublicUserAPITest(TestCase):
    """Test the users api(public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating a user with a valid payload is successfull"""
        payload = {
            "email": "test@django.com",
            "password": "django123",
            "name": "Django Python",
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_create_duplicate_user(self):
        "Test creating a user that already exists"
        payload = {"email": "test@django.com", "password": "django123"}

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test to check password must be more than 5 characters"""
        payload = {"email": "test@django.com", "password": "dj"}

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
                email=payload["email"]
            ).exists()

        self.assertFalse(user_exists)
