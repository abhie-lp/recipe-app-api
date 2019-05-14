from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


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

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            "email": "test@django.com",
            "password": "django123",
        }

        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)

    def test_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email="test@django.com", password="django123")

        payload = {"email": "test@django.com", "password": "wrong"}

        res = self.client.post(TOKEN_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_create_token_without_user(self):
        """Test that no token is created without a user"""
        payload = {"email": "test@django.com", "password": "django123"}

        res = self.client.post(TOKEN_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_create_token_missing_field(self):
        """Test that both email and password are required to create token"""
        res = self.client.post(TOKEN_URL, {"email": "one", "password": ""})

        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_retrieve_user_unauthorised(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email="test@django.com",
            password="django123",
            name="Django Boy",
        )

        self.client = APIClient()

        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged-in user only"""
        res = self.client.get(ME_URL)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, {
            "name": self.user.name,
            "email": self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test that POST method not allowed on me URL"""
        res = self.client.post(ME_URL, {})

        self.assertEquals(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_profile_update(self):
        """Test updating user profile for authenticated user"""
        payload = {
            "name": "New Name",
            "password": "newdjango",
        }

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
