# middleware.py

from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from businessapp.models import BlackListedToken  # Adjust to your actual model location

class TokenValidationMiddleware:
    EXCLUDED_PATHS = ['/login/userlogin/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request path is excluded
        if request.path_info in self.EXCLUDED_PATHS:
            return self.get_response(request)

        # Retrieve the Bearer token from the Authorization header
        authorization_header = request.headers.get('Authorization', '')
        if not authorization_header.startswith('Bearer '):
            return Response({"error": "Invalid Authorization header"}, status=status.HTTP_401_UNAUTHORIZED)

        token = authorization_header[len('Bearer '):]

        # Check if the token is blacklisted
        is_blacklisted = BlackListedToken.objects.filter(token=token).exists()

        if is_blacklisted:
            return Response({"message": "Token is blacklisted"}, status=status.HTTP_401_UNAUTHORIZED)

        # Continue with other checks if needed
        try:
            access_token = AccessToken(token)
            access_token.verify()
        except TokenError:
            return Response({'error': 'Token is invalid or expired'}, status=status.HTTP_401_UNAUTHORIZED)

        response = self.get_response(request)
        return response
