from django.test import TestCase
from django.contrib.auth import get_user_model


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
