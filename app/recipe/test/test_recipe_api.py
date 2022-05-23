from core.models import Recipe, Tag, Ingredient
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


# api/recipe/recipes/
# api/recipe/recipe/1

def detail_url(recipe_id):
    """return a recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main Course'):
    """create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='beef'):
    """create and return ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """create and return sample recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeTestCase(TestCase):
    """test for recipe public endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_list_recipe_require_authentication_failed(self):
        """ will test that recipe endpoints requires authentication"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeTestCase(TestCase):
    """will test the recipe endpoints that requires authentications"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testuser@gmail.com',
            password='testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieving_recipe_for_authenticated_user(self):
        """will rest retrieving recipe list for the authenticated user"""
        test_user = get_user_model().objects.create_user(
            'testuser2@gmail.com',
            'testpass'
        )
        sample_recipe(user=self.user)
        sample_recipe(user=test_user)

        res = self.client.get(RECIPE_URL)
        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_detail_view(self):
        """test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_valid_payload(self):
        """test creating recipe with valid payload successfull"""
        payload = {
            'title': 'Fried Rice',
            'time_minutes': 30,
            'price': 10.00
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['title'], payload['title'])

        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """test creating recipe with tags"""
        tag1 = sample_tag(user=self.user, name='vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')

        payload = {
            'title': 'New Recipe',
            'time_minutes': 5,
            'price': 25,
            'tags': [tag1.id, tag2.id]
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_ingredient(self):
        """test creating recipe with ingredients"""
        ing1 = sample_ingredient(user=self.user, name='maggi')
        ing2 = sample_ingredient(user=self.user, name='salt')

        payload = {
            'title': 'Fried Egg',
            'time_minutes': 3,
            'price': 5.00,
            'ingredients': [ing1.id, ing2.id]
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertIn(ing1, ingredients)
        self.assertIn(ing2, ingredients)
        self.assertEqual(ingredients.count(), 2)
