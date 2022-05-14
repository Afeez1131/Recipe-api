from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    def test_create_user_with_email_successfully(self):
        """This will test a user is created with email is successful"""
        email = "testemail@gmail.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_is_normalize(self):
        """This will test if an email address for a new user is normalized"""
        email = "testemail@GMAIL.COM"
        password = "testpass"
        user = get_user_model().objects.create_user(email, "testpass")
        self.assertEqual(user.email, email.lower())

    def test_create_user_with_invalid_email(self):
        """Test that creating user without an email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "testpass")

    def test_create_superuser_successfully(self):
        """will create a user with admin privileges"""
        email = "testemail@gmail.com"
        password = "testpass123"
        user = get_user_model().objects.create_superuser(email=email, password=password)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
