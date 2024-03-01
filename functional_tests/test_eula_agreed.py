from http import HTTPStatus
from rest_framework.test import APITestCase

from api.models import User


class EulaAgreedTest(APITestCase):
    def test_finds_if_eula_agreed(self):
        user = User.objects.create()
        self.client.force_authenticate(user=user)
        response = self.client.get("/eula-agreed/")
        assert response.status_code == HTTPStatus.OK
        assert not response.data["agreed_to_eula"]

    def test_updates_eula_agreed(self):
        user = User.objects.create()
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            "/eula-agreed/", {"agreed_to_eula": True}, format="json"
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data["agreed_to_eula"]
        user = User.objects.get(pk=user.pk)
        assert user.agreed_to_eula
        response = self.client.patch(
            "/eula-agreed/", {"agreed_to_eula": False}, format="json"
        )
        assert response.status_code == HTTPStatus.OK
        assert not response.data["agreed_to_eula"]
        user = User.objects.get(pk=user.pk)
        assert not user.agreed_to_eula
