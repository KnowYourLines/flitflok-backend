import uuid
from http import HTTPStatus
from rest_framework.test import APITestCase

from api.models import User, Video


class VideoTest(APITestCase):
    def test_submits_video(self):
        user = User.objects.create(username="hello world")
        video_id = uuid.uuid4()
        self.client.force_authenticate(user=user)
        response = self.client.post(
            "/video/",
            {
                "file_id": video_id,
                "place_name": "hello",
                "address": "world",
                "location": {
                    "type": "Point",
                    "coordinates": [-0.0333876462451904, 51.51291201050047],
                },
            },
            format="json",
        )
        assert response.status_code == HTTPStatus.CREATED
        assert response.data == {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [-0.03338764624519, 51.51291201050047],
            },
            "properties": {
                "place_name": "hello",
                "address": "world",
                "file_id": str(video_id),
            },
        }
        saved_video = Video.objects.get(file_id=video_id)
        assert saved_video.location.x == -0.0333876462451904
        assert saved_video.location.y == 51.51291201050047
        assert saved_video.place_name == "hello"
        assert saved_video.address == "world"
