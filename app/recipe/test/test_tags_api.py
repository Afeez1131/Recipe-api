from core.models import Tag
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')


class PublicTagApiTestCase(TestCase):
    """Test the publicly availbale endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_tag_list_require_login(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTestCase(TestCase):
    """Test the endpoints that requires authentication"""

    def setUp(self):
        self.client = APIClient()
        payload = {
            'email': 'testemail@gmail.com',
            'password': 'testpass'
        }
        self.user = get_user_model().objects.create_user(**payload)
        self.client.force_authenticate(self.user)

    def test_retrieve_user_tags(self):
        """Retrieve the list of tags if any"""
        Tag.objects.create(name='Jollof Rice', user=self.user)
        Tag.objects.create(name='Fried Rice', user=self.user)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_authenticated_user_tags(self):
        """will retrieve the list of all tags for an authenticated user"""
        test_user = get_user_model().objects.create_user(
            'testemail3@gmail.com',
            'testpass'
        )
        tag = Tag.objects.create(name='Jollof Rice', user=self.user)
        Tag.objects.create(name='Fried Rice', user=test_user)

        tags = Tag.objects.filter(user=self.user)
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_creating_tag_success(self):
        """Will test creating a new tag with valid payload will be successful"""
        payload = {
            'name': 'test tags',
            'user': self.user.id
        }
        # Tag.objects.create(user = self.user, name=payload['name'])
        self.client.post(TAG_URL, payload)
        exist = Tag.objects.filter(user=self.user, name=payload['name']).exists()
        self.assertTrue(exist)

    def test_creating_tag_invalid_payload(self):
        """will test that creating tags with invalid payload not successfull"""
        payload = {
            'name': ''
        }
        res = self.client.post(TAG_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
