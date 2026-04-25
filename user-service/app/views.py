from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import IsAdmin
from .models import User
from .serializers import AdminUserWriteSerializer, LoginSerializer, RegisterSerializer, UserSerializer


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


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by("id")
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminUserWriteSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all().order_by("id")
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return AdminUserWriteSerializer
        return UserSerializer
