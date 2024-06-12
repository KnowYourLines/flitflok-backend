import os
from http import HTTPStatus

from django.core import mail
from django.test.utils import override_settings
from freezegun import freeze_time
from rest_framework.test import APITestCase

from api.models import User, Video


# @override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
class VideoActionsTest(APITestCase):
    def test_counts_unique_video_direction_requests(self):
        user = User.objects.create(username="hello world")
        video = Video.objects.create(creator=user)
        self.client.force_authenticate(user=user)
        self.client.patch(
            f"/video/{video.id}/",
            {
                "place_name": "hello",
                "address": "world",
                "location": {
                    "type": "Point",
                    "coordinates": [-0.011591, 51.491857],
                },
            },
            format="json",
        )
        response = self.client.patch(
            f"/video/{str(video.id)}/went/",
        )
        assert response.status_code == HTTPStatus.NO_CONTENT
        assert not response.data
        video = Video.objects.get(id=video.id)
        assert video.directions_requested_by.all().first() == user
        assert len(video.directions_requested_by.all()) == 1
        self.client.patch(
            f"/video/{str(video.id)}/went/",
        )
        video = Video.objects.get(id=video.id)
        assert len(video.directions_requested_by.all()) == 1
        user2 = User.objects.create(username="goodbye world")
        self.client.force_authenticate(user=user2)
        self.client.patch(
            f"/video/{str(video.id)}/went/",
        )
        video = Video.objects.all().first()
        assert user in video.directions_requested_by.all()
        assert user2 in video.directions_requested_by.all()
        assert len(video.directions_requested_by.all()) == 2

    def test_reports_video(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        video = Video.objects.create(creator=user, playback_id="1")
        self.client.patch(
            f"/video/{video.id}/",
            {
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
            f"/video/{bad_video_id}/report/",
            format="json",
        )
        assert response.status_code == HTTPStatus.NO_CONTENT
        assert not response.data
        reported_video = Video.objects.get(id=bad_video_id)
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
        video = Video.objects.create(creator=user, playback_id="1")
        self.client.patch(
            f"/video/{video.id}/",
            {
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
            f"/video/{bad_video_id}/hide/",
            format="json",
        )
        assert response.status_code == HTTPStatus.NO_CONTENT
        assert not response.data
        reported_video = Video.objects.get(place_name="hello")
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

    def test_blocks_video_user(self):
        bad_user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=bad_user)
        with freeze_time("2022-01-14"):
            video = Video.objects.create(creator=bad_user, playback_id="1")
            self.client.patch(
                f"/video/{video.id}/",
                {
                    "place_name": "hello",
                    "address": "world",
                    "location": {
                        "type": "Point",
                        "coordinates": [-0.0333876462451904, 51.51291201050047],
                    },
                },
                format="json",
            )
        with freeze_time("2022-01-15"):
            video = Video.objects.create(creator=bad_user, playback_id="2")
            self.client.patch(
                f"/video/{video.id}/",
                {
                    "place_name": "hello2",
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
        user = User.objects.create(username="goodbye world")
        self.client.force_authenticate(user=user)
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
        )
        videos = response.data["features"]
        bad_video_id = videos[-1]["id"]
        response = self.client.patch(
            f"/video/{bad_video_id}/block/",
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == [video["id"] for video in videos]
        assert len(Video.objects.filter(creator=bad_user)) == 2
        user = User.objects.get(username=user.username)
        assert user.blocked_users.all().first() == bad_user
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
        )
        assert response.data == {
            "type": "FeatureCollection",
            "features": [],
        }
        user = User.objects.create(username="new world")
        self.client.force_authenticate(user=user)
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
        )
        assert response.data["features"][-1]["id"] == bad_video_id

    def test_cannot_block_yourself(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        with freeze_time("2022-01-14"):
            video = Video.objects.create(creator=user, playback_id="1")
            self.client.patch(
                f"/video/{video.id}/",
                {
                    "place_name": "hello",
                    "address": "world",
                    "location": {
                        "type": "Point",
                        "coordinates": [-0.0333876462451904, 51.51291201050047],
                    },
                },
                format="json",
            )
        with freeze_time("2022-01-15"):
            video = Video.objects.create(creator=user, playback_id="2")
            self.client.patch(
                f"/video/{video.id}/",
                {
                    "place_name": "hello2",
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
            f"/video/{bad_video_id}/block/",
            format="json",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert set(response.data) == {"creator"}
        assert response.data["creator"][0] == "You cannot block yourself"
