import datetime
import os
import uuid
from http import HTTPStatus

from django.core import mail
from django.test.utils import override_settings
from freezegun import freeze_time
from rest_framework.test import APITestCase

from api.models import User, Video

VALID_FILE_ID = "0888bcb9-c5b1-4587-8ed8-1aed45a04313"
VALID_FILE_ID_2 = "09991e04-1ef9-4a8e-ac94-8a19faa2de1b"
VALID_FILE_ID_3 = "0dbc46ba-f87a-4ff0-a737-e0538c70c4ef"
VALID_FILE_ID_4 = "13d4a295-9949-4d9c-8c46-1d963051e6ec"
VALID_FILE_ID_5 = "1670388e-3d3d-470b-ad7a-779261fc3017"


# @override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
class VideoTest(APITestCase):
    def test_submits_video(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        response = self.client.post(
            "/video/",
            {
                "file_id": VALID_FILE_ID,
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
                "file_id": VALID_FILE_ID,
            },
        }
        saved_video = Video.objects.get(file_id=VALID_FILE_ID)
        assert saved_video.location.x == -0.0333876462451904
        assert saved_video.location.y == 51.51291201050047
        assert saved_video.place_name == "hello"
        assert saved_video.address == "world"

    def test_submitted_video_file_must_exist(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        video_id = uuid.uuid4()
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
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert not Video.objects.filter(file_id=str(video_id))
        assert set(response.data) == {"file_id"}
        assert response.data["file_id"][0] == "File does not exist"

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

    def test_finds_next_2_videos(self):
        with freeze_time("2012-01-14"):
            user = User.objects.create(username="hello world")
            self.client.force_authenticate(user=user)
            self.client.post(
                "/video/",
                {
                    "file_id": VALID_FILE_ID,
                    "place_name": "hello",
                    "address": "world",
                    "location": {
                        "type": "Point",
                        "coordinates": [-0.0333876462451904, 51.51291201050047],
                    },
                },
                format="json",
            )
        with freeze_time("2022-01-14"):
            self.client.post(
                "/video/",
                {
                    "file_id": VALID_FILE_ID_2,
                    "place_name": "hello",
                    "address": "world",
                    "location": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                },
                format="json",
            )
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
                    "id": str(Video.objects.get(file_id=VALID_FILE_ID).id),
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.03338764624519, 51.51291201050047],
                    },
                    "properties": {
                        "place_name": "hello",
                        "address": "world",
                        "file_id": VALID_FILE_ID,
                        "distance": 0.0,
                        "posted_at": datetime.datetime(
                            2012, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                    },
                },
                {
                    "type": "Feature",
                    "id": str(Video.objects.get(file_id=VALID_FILE_ID_2).id),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                    "properties": {
                        "place_name": "hello",
                        "address": "world",
                        "file_id": VALID_FILE_ID_2,
                        "distance": 2.788929913358129,
                        "posted_at": datetime.datetime(
                            2022, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                    },
                },
            ],
        }
        with freeze_time("2022-01-14"):
            self.client.post(
                "/video/",
                {
                    "file_id": VALID_FILE_ID_3,
                    "place_name": "hello",
                    "address": "world",
                    "location": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                },
                format="json",
            )
        with freeze_time("2022-02-14"):
            self.client.post(
                "/video/",
                {
                    "file_id": VALID_FILE_ID_4,
                    "place_name": "hello",
                    "address": "world",
                    "location": {
                        "type": "Point",
                        "coordinates": [-3.188267, 55.953251],
                    },
                },
                format="json",
            )
        with freeze_time("2022-01-15"):
            self.client.post(
                "/video/",
                {
                    "file_id": VALID_FILE_ID_5,
                    "place_name": "hello",
                    "address": "world",
                    "location": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                },
                format="json",
            )
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
            f"&current_video={response.data['features'][-1]['id']}"
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": str(Video.objects.get(file_id=VALID_FILE_ID_5).id),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                    "properties": {
                        "place_name": "hello",
                        "address": "world",
                        "file_id": VALID_FILE_ID_5,
                        "distance": 251.75032594284824,
                        "posted_at": datetime.datetime(
                            2022, 1, 15, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                    },
                },
                {
                    "id": str(Video.objects.get(file_id=VALID_FILE_ID_3).id),
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                    "properties": {
                        "place_name": "hello",
                        "address": "world",
                        "file_id": VALID_FILE_ID_3,
                        "distance": 251.75032594284824,
                        "posted_at": datetime.datetime(
                            2022, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                    },
                },
            ],
        }
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
            f"&current_video={response.data['features'][-1]['id']}"
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": str(Video.objects.get(file_id=VALID_FILE_ID_4).id),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-3.188267, 55.953251],
                    },
                    "properties": {
                        "place_name": "hello",
                        "address": "world",
                        "file_id": VALID_FILE_ID_4,
                        "distance": 536.136057408564,
                        "posted_at": datetime.datetime(
                            2022, 2, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                    },
                },
            ],
        }
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
            f"&current_video={response.data['features'][-1]['id']}"
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == {
            "type": "FeatureCollection",
            "features": [],
        }

    def test_current_video_must_be_valid(self):
        current_latitude = 51.51291201050047
        current_longitude = -0.0333876462451904
        user = User.objects.create(username="hello world")
        current_video = uuid.uuid4()
        self.client.force_authenticate(user=user)
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
            f"&current_video={current_video}"
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert set(response.data) == {"current_video"}
        assert response.data["current_video"][0] == "Current video does not exist"

    def test_reports_video(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        self.client.post(
            "/video/",
            {
                "file_id": VALID_FILE_ID,
                "place_name": "hello",
                "address": "world",
                "location": {
                    "type": "Point",
                    "coordinates": [-0.0333876462451904, 51.51291201050047],
                },
            },
            format="json",
        )
        current_latitude = 51.51291201050047
        current_longitude = -0.0333876462451904
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
        )
        bad_video_id = response.data["features"][-1]["id"]
        response = self.client.patch(
            f"/video/{bad_video_id}/",
            {"reported": True},
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [-0.03338764624519, 51.51291201050047],
            },
            "properties": {
                "place_name": "hello",
                "address": "world",
                "file_id": VALID_FILE_ID,
            },
        }
        reported_video = Video.objects.get(file_id=VALID_FILE_ID)
        assert reported_video.reported_by.all().first() == user
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
        )
        assert response.data == {
            "type": "FeatureCollection",
            "features": [],
        }
        user = User.objects.create(username="goodbye world")
        self.client.force_authenticate(user=user)
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
        )
        assert response.data["features"][-1]["id"] == bad_video_id
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Video reported"
        assert mail.outbox[0].to == [os.environ.get("EMAIL_HOST_USER")]
        assert (
            mail.outbox[0].from_email
            == f"FlitFlok <{os.environ.get('EMAIL_HOST_USER')}>"
        )

    def test_hides_video(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        self.client.post(
            "/video/",
            {
                "file_id": VALID_FILE_ID,
                "place_name": "hello",
                "address": "world",
                "location": {
                    "type": "Point",
                    "coordinates": [-0.0333876462451904, 51.51291201050047],
                },
            },
            format="json",
        )
        current_latitude = 51.51291201050047
        current_longitude = -0.0333876462451904
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
        )
        bad_video_id = response.data["features"][-1]["id"]
        response = self.client.patch(
            f"/video/{bad_video_id}/",
            {"hidden": True},
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [-0.03338764624519, 51.51291201050047],
            },
            "properties": {
                "place_name": "hello",
                "address": "world",
                "file_id": VALID_FILE_ID,
            },
        }
        reported_video = Video.objects.get(file_id=VALID_FILE_ID)
        assert reported_video.hidden_from.all().first() == user
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
        )
        assert response.data == {
            "type": "FeatureCollection",
            "features": [],
        }
        user = User.objects.create(username="goodbye world")
        self.client.force_authenticate(user=user)
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
        )
        assert response.data["features"][-1]["id"] == bad_video_id

    def test_only_allow_either_hide_or_report(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        self.client.post(
            "/video/",
            {
                "file_id": VALID_FILE_ID,
                "place_name": "hello",
                "address": "world",
                "location": {
                    "type": "Point",
                    "coordinates": [-0.0333876462451904, 51.51291201050047],
                },
            },
            format="json",
        )
        current_latitude = 51.51291201050047
        current_longitude = -0.0333876462451904
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
        )
        bad_video_id = response.data["features"][-1]["id"]
        response = self.client.patch(
            f"/video/{bad_video_id}/",
            {"reported": True, "hidden": True},
            format="json",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert (
            response.data["non_field_errors"][0]
            == "Video cannot be both reported and hidden"
        )
        response = self.client.patch(
            f"/video/{bad_video_id}/",
            {},
            format="json",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert (
            response.data["non_field_errors"][0]
            == "Video must be either reported or hidden"
        )
