import datetime
import uuid
from http import HTTPStatus

from freezegun import freeze_time
from rest_framework.test import APITestCase

from api.models import User, Video


class VideoResultsTest(APITestCase):
    def test_filters_by_location_purpose(self):
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
                    "location_purpose": "Food & Drink",
                },
                format="json",
            )
        Video.objects.create(creator=user, playback_id="2")
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
                    "location_purpose": "Food & Drink",
                },
                format="json",
            )
        current_latitude = 51.51291201050047
        current_longitude = -0.0333876462451904
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}&purpose="
            f"Food%20%26%20Drink"
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
                        "location_purpose": "Food & Drink",
                    },
                },
            ],
        }

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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
                        "location_purpose": "",
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
