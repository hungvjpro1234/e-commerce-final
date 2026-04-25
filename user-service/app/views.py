from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

