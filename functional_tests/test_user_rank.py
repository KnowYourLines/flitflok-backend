from http import HTTPStatus
from rest_framework.test import APITestCase

from api.models import User, Video

VALID_FILE_ID = "0888bcb9-c5b1-4587-8ed8-1aed45a04313"


class UserRankingTest(APITestCase):
    def test_gets_latest_user_ranking(self):
        user = User.objects.create(username="hello world")
        user2 = User.objects.create(username="goodbye world")
        self.client.force_authenticate(user=user)
        response = self.client.get("/rank/")
        assert response.status_code == HTTPStatus.OK
        assert response.data == {"rank": 1, "points": 0}
        self.client.force_authenticate(user=user2)
        response = self.client.get("/rank/")
        assert response.data == {"rank": 1, "points": 0}
        video = Video.objects.create(creator=user2)
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
        response = self.client.get("/rank/")
        assert response.data == {"rank": 1, "points": 10000}
        self.client.force_authenticate(user=user)
        response = self.client.get("/rank/")
        assert response.data == {"rank": 2, "points": 0}
