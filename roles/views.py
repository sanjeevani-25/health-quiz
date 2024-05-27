# from django.shortcuts import render

# # Create your views here.
# from django.http import HttpResponse

# def index(request):
#     return HttpResponse("Welcome to the Roles app!")

# from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import *
from .serializer import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            response_data = {
                "token": token,
                "user": serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    last_login = models.DateTimeField(auto_now=True)

    def create(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.get(email=email)
        if user is None:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        if user.check_password(password):
            print(user.last_login)
            print(self.last_login)
            user.last_login = self.last_login
            user.save()
            token = get_tokens_for_user(user)
            return Response({"token": token, "message": "Login Successful", "user":user.type, "uid":user.uid}, status=status.HTTP_200_OK)
        return Response({"message": "Login Failed"}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
