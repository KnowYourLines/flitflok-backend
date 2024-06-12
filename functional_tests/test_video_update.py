from http import HTTPStatus


from rest_framework.test import APITestCase

from api.models import User, Video


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
