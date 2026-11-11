from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User.objects.create_user(
            **validated_data,
            password=password,
            role=User.Role.EMPLOYEE
        )

        return user


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
        ]

        read_only_fields = ['id', 'username', 'role']
