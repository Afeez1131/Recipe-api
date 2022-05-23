from core.models import Ingredient
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


def sample_user(email='testuser@gmail.com', password='testpass'):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientApiTest(TestCase):
    """test the ingredient """

    def setUp(self):
        self.client = APIClient()

    def test_ingredient_list_require_login(self):
        """test that ingredient listing endpoint requires user to login"""
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """test the endpoints that requires authentication"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='testemail@gmail.com',
                                                         password='testpass')
        self.client.force_authenticate(self.user)

    def test_ingredient_list(self):
        """will test listing all ingredients after login"""
        Ingredient.objects.create(
            name='onion',
            user=self.user
        )

        Ingredient.objects.create(
            name='Tomato paste',
            user=self.user
        )

        res = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_ingredient_limited_to_authenticated_user(self):
        """ test that ingredient by authenticated user only will be listed"""
        test_user = get_user_model().objects.create_user(
            email='testuser@gmail.com',
            password='testpass'
        )
        Ingredient.objects.create(
            name='Tomato paste',
            user=self.user
        )

        ingredient = Ingredient.objects.create(
            name='Tomato paste',
            user=test_user
        )

        res = self.client.get(INGREDIENT_URL)
        # ingredient = Ingredient.objects.filter(user=self.user).exists()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(len(res.data), 1)

    def test_creating_ingredient_valid_payload_success(self):
        """will create a new ingredient successfully with valid payload"""
        payload = {
            'name': 'onion',
            'user': self.user
        }
        res = self.client.post(INGREDIENT_URL, payload)
        exist = Ingredient.objects.filter(user=self.user, name=payload['name']).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exist)

    def test_creating_ingredient_invalid_payload_failed(self):
        """test that creating ingredient without a valid payload will fail"""
        payload = {'name': ''}

        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

