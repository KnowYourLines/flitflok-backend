from http import HTTPStatus

from firebase_admin import auth
from rest_framework.test import APITestCase

from api.models import User


class AccountDeletionTest(APITestCase):
    def test_deletes_user(self):
        firebase_user = auth.create_user()
        uid = firebase_user.uid
        user = User.objects.create(username=uid)
        self.client.force_authenticate(user=user)
        response = self.client.delete("/delete-account/")
        assert response.status_code == HTTPStatus.NO_CONTENT
        assert not User.objects.filter(username=uid)
        deleted_firebase_users = auth.get_users([auth.UidIdentifier(uid)]).not_found
        assert len(deleted_firebase_users) == 1
        assert deleted_firebase_users[0].uid == uid
