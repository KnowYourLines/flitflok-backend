from rest_framework.test import APITestCase

from api.models import User, Video

VALID_FILE_ID = "0888bcb9-c5b1-4587-8ed8-1aed45a04313"
VALID_FILE_ID_2 = "09991e04-1ef9-4a8e-ac94-8a19faa2de1b"
VALID_FILE_ID_3 = "0dbc46ba-f87a-4ff0-a737-e0538c70c4ef"
VALID_FILE_ID_4 = "13d4a295-9949-4d9c-8c46-1d963051e6ec"


class PointsTest(APITestCase):
    def test_points_for_new_video_with_no_videos_1mi_around(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        video = Video.objects.create(creator=user)
        self.client.patch(
            f"/video/{video.id}/",
            {
                "location": {
                    "type": "Point",
                    "coordinates": [-0.0333876462451904, 51.51291201050047],
                },
            },
            format="json",
        )
        assert user.points == 10000
        self.client.patch(
            f"/video/{video.id}/",
            {
                "location": {
                    "type": "Point",
                    "coordinates": [-0.0333876462451904, 51.51291201050047],
                },
            },
            format="json",
        )
        assert user.points == 10000

    def test_existing_videos_1mi_around_boost_points_for_direction_requests(self):
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        video = Video.objects.create(creator=user)
        self.client.patch(
            f"/video/{video.id}/",
            {
                "location": {
                    "type": "Point",
                    "coordinates": [-0.0333876462451904, 51.51291201050047],
                },
            },
            format="json",
        )
        self.client.patch(
            f"/video/{str(video.id)}/went/",
        )
        assert user.points == 10000
        video2 = Video.objects.create(creator=user)
        self.client.patch(
            f"/video/{video2.id}/",
            {
                "location": {
                    "type": "Point",
                    "coordinates": [-0.0333876462451904, 51.51291201050047],
                },
            },
            format="json",
        )
        user2 = User.objects.create(username="goodbye world")
        self.client.force_authenticate(user=user2)
        self.client.patch(
            f"/video/{str(video.id)}/went/",
        )
        user = User.objects.get(username="hello world")
        assert user.points == 10010
        video3 = Video.objects.create(creator=user2)
        self.client.patch(
            f"/video/{video3.id}/",
            {
                "location": {
                    "type": "Point",
                    "coordinates": [-0.0333876462451904, 51.51291201050047],
                },
            },
            format="json",
        )
        video4 = Video.objects.create(creator=user2)
        self.client.patch(
            f"/video/{video4.id}/",
            {
                "location": {
                    "type": "Point",
                    "coordinates": [-0.0333876462451904, 51.51291201050047],
                },
            },
            format="json",
        )
        user3 = User.objects.create(username="hello again")
        self.client.force_authenticate(user=user3)
        self.client.patch(
            f"/video/{str(video.id)}/went/",
        )
        user = User.objects.get(username="hello world")
        assert user.points == 10030
