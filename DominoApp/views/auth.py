import secrets

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password

from ..models import User, AuthToken


@api_view(['POST'])
def login(request):

    email = request.data.get("UserEmail")
    password = request.data.get("UserPassword")
    if not email or not password:
        return Response(
            {"error": "UserEmail and UserPassword are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(UserEmail=email)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )


    if not check_password(password, user.UserPassword):
        return Response(
            {"error": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )

 
    token_key = secrets.token_hex(20)
    token = AuthToken.objects.create(
        UserId=user,
        TokenKey=token_key
    )


    return Response(
        {
            "token": token.TokenKey,
            "userId": user.UserId,
            "role": user.UserRole,
        },
        status=status.HTTP_200_OK
    )
