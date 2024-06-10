from firebase_admin import auth
from rest_framework.test import APITestCase

from api.models import User, Video
from http import HTTPStatus


class VideoUploadTest(APITestCase):
    def test_get_upload_url(self):
        user = User.objects.create(username="zVAvUkRbSbgZCSnZ64hU9PyutCi1")
        self.client.force_authenticate(user=user)
        response = self.client.get(
            "/video-upload/",
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data["properties"]["url"].startswith(
            "https://storage.googleapis.com/video-storage-gcp"
        )
        assert Video.objects.get(id=response.data["properties"]["passthrough"])

    def test_must_be_verified_to_upload(self):
        firebase_user = auth.create_user()
        uid = firebase_user.uid
        user = User.objects.create(username=uid)
        self.client.force_authenticate(user=user)
        response = self.client.get(
            "/video-upload/",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data["creator"][0] == "Verified email address required"
        auth.delete_user(uid)
