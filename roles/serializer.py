from dataclasses import fields
from .models import User
from .models import *
from rest_framework import serializers
# from quiz.serializer import QuizSerializer


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
        # fields = ['uid', 'first_name', 'email', 'role']
        # depth = 2

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uid', 'first_name', 'email', 'role']
        # depth = 2
