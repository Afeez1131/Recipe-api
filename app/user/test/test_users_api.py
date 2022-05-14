from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create(**params)


class PublicUserApiTest(TestCase):
    """Test the users publicly accessible endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ test that user is created with valid payload successfull"""
        payload = {
            'email': 'testemail@gmail.com',
            'password': 'testpass',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exist(self):
        """test creating an already existing user fails"""

        payload = {
            'email': 'testemail@gmail.com',
            'password': 'testpass',
            'name': 'Test Name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_short(self):
        """ test that the password is more than 5 chars"""
        payload = {
            'email': 'testemail@gmail.com',
            'password': 'tes',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exist)

    def test_user_creation_fail_without_email(self):
        """Test that creating a user without the supply of email will fail"""
        payload = {
            'email': '',
            'password': 'tes',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        """test that token is created for user successfully"""
        payload = {
            'email': 'admin@gmail.com',
            'password': 'testpass',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        print(res, res.data)
        # self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_user_token_invalid_data(self):
        """Test creating user token with invalid credentials, Token will not be created"""

        create_user(email='test@mail.com', password='testpass')
        payload = {
            'email': 'test@mail.com',
            'password': 'password',
            'name': 'Test Name'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_without_user(self):
        """Test token is not created if user does not exist"""
        res = self.client.post(TOKEN_URL)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_without_password(self):
        """Test that token is not created for a user without password"""
        payload = {
            'email': 'test@mail.com',
            'password': '',
            'name': 'Test Name'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_without_email(self):
        """Test that token is not created for a user without email"""
        payload = {
            'email': '',
            'password': 'testpass',
            'name': 'Test Name'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
