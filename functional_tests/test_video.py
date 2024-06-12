import datetime
import os
import uuid
from http import HTTPStatus

from django.core import mail
from django.test.utils import override_settings
from freezegun import freeze_time
from rest_framework.test import APITestCase

from api.models import User, Video


# @override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
class VideoUpdateTest(APITestCase):
    def test_adds_video_details(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        video = Video.objects.create(creator=user)
        response = self.client.patch(
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
            },
        }
        saved_video = Video.objects.get(id=video.id)
        assert saved_video.location.x == -0.0333876462451904
        assert saved_video.location.y == 51.51291201050047
        assert saved_video.place_name == "hello"
        assert saved_video.address == "world"

    def test_must_be_video_creator(self):
        user = User.objects.create(username="hello world")
        user2 = User.objects.create(username="hello world2")
        self.client.force_authenticate(user=user)
        video = Video.objects.create(creator=user2)
        response = self.client.patch(
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
        assert response.status_code == HTTPStatus.FORBIDDEN

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

    def test_omits_videos_without_playback_id(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        video = Video.objects.create(creator=user, playback_id="1")
        with freeze_time("2012-01-14"):
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
        Video.objects.create(creator=user)
        Video.objects.create(creator=user, playback_id="")
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
                    "id": str(Video.objects.get(place_name="hello").id),
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.03338764624519, 51.51291201050047],
                    },
                    "properties": {
                        "place_name": "hello",
                        "address": "world",
                        "distance": "0.0 km",
                        "posted_at": datetime.datetime(
                            2012, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "1",
                    },
                },
            ],
        }

    def test_orders_by_distance_creator_points_timestamp(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        with freeze_time("2012-01-14"):
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
        with freeze_time("2012-01-14"):
            video = Video.objects.create(creator=user, playback_id="2")
            self.client.patch(
                f"/video/{video.id}/",
                {
                    "place_name": "hello2",
                    "address": "world",
                    "location": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                },
                format="json",
            )
        user2 = User.objects.create(username="goodbye world")
        self.client.force_authenticate(user=user2)
        with freeze_time("2023-01-14"):
            video = Video.objects.create(creator=user2, playback_id="3")
            self.client.patch(
                f"/video/{video.id}/",
                {
                    "place_name": "hello3",
                    "address": "world",
                    "location": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                },
                format="json",
            )
        self.client.force_authenticate(user=user)
        with freeze_time("2023-01-14"):
            video = Video.objects.create(creator=user, playback_id="4")
            self.client.patch(
                f"/video/{video.id}/",
                {
                    "place_name": "hello4",
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
        assert response.data == {
            "type": "FeatureCollection",
            "features": [
                {
                    "id": str(Video.objects.get(place_name="hello").id),
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.03338764624519, 51.51291201050047],
                    },
                    "properties": {
                        "place_name": "hello",
                        "address": "world",
                        "distance": "0.0 km",
                        "posted_at": datetime.datetime(
                            2012, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "1",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(Video.objects.get(place_name="hello4").id),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                    "properties": {
                        "place_name": "hello4",
                        "address": "world",
                        "distance": "2.8 km",
                        "posted_at": datetime.datetime(
                            2023, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "4",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(Video.objects.get(place_name="hello2").id),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                    "properties": {
                        "place_name": "hello2",
                        "address": "world",
                        "distance": "2.8 km",
                        "posted_at": datetime.datetime(
                            2012, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "2",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(Video.objects.get(place_name="hello3").id),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                    "properties": {
                        "place_name": "hello3",
                        "address": "world",
                        "distance": "2.8 km",
                        "posted_at": datetime.datetime(
                            2023, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "goodbye world",
                        "creator_rank": 2,
                        "display_name": None,
                        "playback_id": "3",
                    },
                },
            ],
        }

    def test_finds_next_5_videos(self):
        with freeze_time("2012-01-14"):
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
        with freeze_time("2022-01-14"):
            video = Video.objects.create(creator=user, playback_id="2")
            self.client.patch(
                f"/video/{video.id}/",
                {
                    "place_name": "hello2",
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
                    "id": str(Video.objects.get(place_name="hello").id),
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.03338764624519, 51.51291201050047],
                    },
                    "properties": {
                        "place_name": "hello",
                        "address": "world",
                        "distance": "0.0 km",
                        "posted_at": datetime.datetime(
                            2012, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "1",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(Video.objects.get(place_name="hello2").id),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                    "properties": {
                        "place_name": "hello2",
                        "address": "world",
                        "distance": "2.8 km",
                        "posted_at": datetime.datetime(
                            2022, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "2",
                    },
                },
            ],
        }
        with freeze_time("2022-01-14"):
            video = Video.objects.create(creator=user, playback_id="3")
            self.client.patch(
                f"/video/{video.id}/",
                {
                    "place_name": "hello3",
                    "address": "world",
                    "location": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                },
                format="json",
            )
        with freeze_time("2022-02-14"):
            video = Video.objects.create(creator=user, playback_id="4")
            self.client.patch(
                f"/video/{video.id}/",
                {
                    "place_name": "hello4",
                    "address": "world",
                    "location": {
                        "type": "Point",
                        "coordinates": [-3.188267, 55.953251],
                    },
                },
                format="json",
            )
        with freeze_time("2022-01-15"):
            video = Video.objects.create(creator=user, playback_id="5")
            self.client.patch(
                f"/video/{video.id}/",
                {
                    "place_name": "hello5",
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
                    "id": str(Video.objects.get(place_name="hello5").id),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                    "properties": {
                        "place_name": "hello5",
                        "address": "world",
                        "distance": "251.8 km",
                        "posted_at": datetime.datetime(
                            2022, 1, 15, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "5",
                    },
                },
                {
                    "id": str(Video.objects.get(place_name="hello3").id),
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                    "properties": {
                        "place_name": "hello3",
                        "address": "world",
                        "distance": "251.8 km",
                        "posted_at": datetime.datetime(
                            2022, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "3",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(Video.objects.get(place_name="hello4").id),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-3.188267, 55.953251],
                    },
                    "properties": {
                        "place_name": "hello4",
                        "address": "world",
                        "distance": "536.1 km",
                        "posted_at": datetime.datetime(
                            2022, 2, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "4",
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
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == {
            "type": "FeatureCollection",
            "features": [
                {
                    "id": str(Video.objects.get(place_name="hello").id),
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.03338764624519, 51.51291201050047],
                    },
                    "properties": {
                        "place_name": "hello",
                        "address": "world",
                        "distance": "0.0 km",
                        "posted_at": datetime.datetime(
                            2012, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "1",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(Video.objects.get(place_name="hello2").id),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                    "properties": {
                        "place_name": "hello2",
                        "address": "world",
                        "distance": "2.8 km",
                        "posted_at": datetime.datetime(
                            2022, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "2",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(Video.objects.get(place_name="hello5").id),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                    "properties": {
                        "place_name": "hello5",
                        "address": "world",
                        "distance": "251.8 km",
                        "posted_at": datetime.datetime(
                            2022, 1, 15, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "5",
                    },
                },
                {
                    "id": str(Video.objects.get(place_name="hello3").id),
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                    "properties": {
                        "place_name": "hello3",
                        "address": "world",
                        "distance": "251.8 km",
                        "posted_at": datetime.datetime(
                            2022, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "3",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(Video.objects.get(place_name="hello4").id),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-3.188267, 55.953251],
                    },
                    "properties": {
                        "place_name": "hello4",
                        "address": "world",
                        "distance": "536.1 km",
                        "posted_at": datetime.datetime(
                            2022, 2, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "playback_id": "4",
                    },
                },
            ],
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
