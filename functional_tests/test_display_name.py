from http import HTTPStatus
from rest_framework.test import APITestCase

from api.models import User


class DisplayNameTest(APITestCase):
    def test_finds_display_name(self):
        user = User.objects.create()
        self.client.force_authenticate(user=user)
        response = self.client.get("/display-name/")
        assert response.status_code == HTTPStatus.OK
        assert response.data == {"display_name": None}

    def test_updates_display_name(self):
        user = User.objects.create()
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            "/display-name/", {"display_name": "hello"}, format="json"
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == {"display_name": "hello"}

    def test_display_name_must_be_unique(self):
        User.objects.create(display_name="hello", username="world")
        user2 = User.objects.create()
        self.client.force_authenticate(user=user2)
        response = self.client.patch(
            "/display-name/", {"display_name": "hello"}, format="json"
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert (
            response.data["display_name"][0]
            == "user with this display name already exists."
        )
