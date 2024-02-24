import logging
import os

import firebase_admin
from firebase_admin import credentials, auth
from rest_framework import authentication

from api.exceptions import InvalidAuthToken, FirebaseError, NoAuthToken
from api.models import User

logger = logging.getLogger(__name__)
cred = credentials.Certificate(
    {
        "type": "service_account",
        "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
        "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_CERT_URL"),
    }
)

default_app = firebase_admin.initialize_app(cred)


class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            raise NoAuthToken()
        token = auth_header.split(" ").pop()
        try:
            decoded_token = auth.verify_id_token(token)
        except auth.RevokedIdTokenError as exc:
            raise InvalidAuthToken(str(exc))
        except auth.UserDisabledError as exc:
            raise InvalidAuthToken(str(exc))
        except auth.InvalidIdTokenError as exc:
            raise InvalidAuthToken(str(exc))

        try:
            uid = decoded_token.get("uid")
        except Exception:
            raise FirebaseError("Missing uid.")
        user, created = User.objects.get_or_create(
            username=uid,
        )
        return user, None
