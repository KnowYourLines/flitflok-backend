from rest_framework.test import APITestCase

from api.models import User, Video
from http import HTTPStatus


class VideoUploadTest(APITestCase):
    def test_get_upload_url(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        response = self.client.get(
            "/video-upload/",
        )
        assert response.status_code == HTTPStatus.CREATED
        assert response.data["properties"]["url"].startswith(
            "https://storage.googleapis.com/video-storage-gcp"
        )
        assert Video.objects.get(id=response.data["properties"]["passthrough"])
