from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""
    # password = serializers.CharField(
    #     style={'input_type': 'password'},
    #     trim_whitespace=False
    # )

    class Meta:
        model = get_user_model()
        fields = ('email', 'name', 'password')
        extra_kwargs = {
            'password': {'write_only': True,
                         'min_length': 5}
        }

    def create(self, validated_data):
        """create a new user with encrypted password and returns it"""
        return get_user_model().objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """validate and authenticate user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(request=self.context.get('request'),
                            username=email,
                            password=password)
        if not user:
            msg = _('Email or Password is incorrect')
            raise serializers.ValidationError(msg, code='authentication')
        attrs['user'] = user
        return attrs

