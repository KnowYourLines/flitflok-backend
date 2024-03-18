import datetime
import uuid
from http import HTTPStatus

from freezegun import freeze_time
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

    def test_requires_file_and_location_only(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        response = self.client.post(
            "/video/",
            {},
            format="json",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert set(response.data) == {"file_id", "location"}
        assert response.data["file_id"][0] == "This field is required."
        assert response.data["location"][0] == "This field is required."

    def test_finds_top_2_videos(self):
        with freeze_time("2012-01-14"):
            user = User.objects.create(username="hello world")
            most_recent_video_id = uuid.uuid4()
            self.client.force_authenticate(user=user)
            response = self.client.post(
                "/video/",
                {
                    "file_id": most_recent_video_id,
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
            second_most_recent_video_id = uuid.uuid4()
            response = self.client.post(
                "/video/",
                {
                    "file_id": second_most_recent_video_id,
                    "place_name": "hello",
                    "address": "world",
                    "location": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                },
                format="json",
            )
            assert response.status_code == HTTPStatus.CREATED
            latest_video_id = uuid.uuid4()
            response = self.client.post(
                "/video/",
                {
                    "file_id": latest_video_id,
                    "place_name": "hello",
                    "address": "world",
                    "location": {
                        "type": "Point",
                        "coordinates": [0, 51.51291201050047],
                    },
                },
                format="json",
            )
            assert response.status_code == HTTPStatus.CREATED
            current_latitude = 51.51291201050047
            current_longitude = -0.0333876462451904
            response = self.client.get(
                f"/video/?latitude={current_latitude}&longitude={current_longitude}"
            )
            assert response.status_code == HTTPStatus.OK
            assert response.data == {
                "type": "FeatureCollection",
                "features": [
                    {
                        "id": str(Video.objects.get(file_id=most_recent_video_id).id),
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-0.03338764624519, 51.51291201050047],
                        },
                        "properties": {
                            "place_name": "hello",
                            "address": "world",
                            "file_id": str(most_recent_video_id),
                            "distance": 0.0,
                            "posted_at": datetime.datetime(
                                2012, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                            ),
                        },
                    },
                    {
                        "type": "Feature",
                        "id": str(Video.objects.get(file_id=latest_video_id).id),
                        "geometry": {
                            "type": "Point",
                            "coordinates": [0.0, 51.51291201050047],
                        },
                        "properties": {
                            "place_name": "hello",
                            "address": "world",
                            "file_id": str(latest_video_id),
                            "distance": 2.3178001882955614,
                            "posted_at": datetime.datetime(
                                2012, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                            ),
                        },
                    },
                ],
            }
