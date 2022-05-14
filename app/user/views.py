from django.shortcuts import render
from .serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.generics import CreateAPIView

class CreateUserView(CreateAPIView):
    """View for creating a new user"""
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """create new authentication token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
