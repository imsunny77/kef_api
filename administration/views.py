from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from administration.serializers import RegisterSerializer, LoginSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "User registered successfully",
                    "data": {
                        "access_token": str(refresh.access_token),
                        "refresh_token": str(refresh),
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "user_type": user.user_type,
                        },
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Login successful",
                    "data": {
                        "access_token": str(refresh.access_token),
                        "refresh_token": str(refresh),
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "user_type": user.user_type,
                        },
                    },
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
