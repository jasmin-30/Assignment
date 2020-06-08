from rest_framework import serializers
from .models import User, Information


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # noinspection PyPackageRequirements
        fields = [
            'first_name',
            'last_name',
            'email',
            'contact',
            'city',
            'DOB'
        ]


class InformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information
        fields = [
            'id',
            'auth_id',
            'info'
        ]
