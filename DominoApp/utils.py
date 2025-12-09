from rest_framework.response import Response
from rest_framework import status

from .models import AuthToken


def get_authenticated_user(request, required_role=None):

    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return None, Response(
            {"error": "Authorization header missing"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        auth_type, token = auth_header.split()
    except ValueError:
        return None, Response(
            {"error": "Invalid Authorization header format"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if auth_type != "Token":
        return None, Response(
            {"error": "Authorization must start with 'Token'"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        auth_token = AuthToken.objects.get(TokenKey=token)
    except AuthToken.DoesNotExist:
        return None, Response(
            {"error": "Invalid token"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    user = auth_token.UserId

    if required_role and user.UserRole != required_role:
        return None, Response(
            {"error": "Insufficient permissions"},
            status=status.HTTP_403_FORBIDDEN
        )

    return user, None
