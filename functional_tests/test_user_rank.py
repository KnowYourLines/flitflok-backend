import datetime
from http import HTTPStatus
from unittest.mock import patch

from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase

from api.models import User
from api.permissions import IsFromCloudflare


class UserRankingTest(APITestCase):
    @patch.object(IsFromCloudflare, "has_permission")
    def test_gets_latest_user_ranking(self, mock_has_permission):
        mock_has_permission.return_value = True
        user = User.objects.create(username="hello world")
        user2 = User.objects.create(username="0dSkRQUJmuUnf5mdDOUr7bxRP1a2")
        self.client.force_authenticate(user=user)
        response = self.client.get("/rank/")
        assert response.status_code == HTTPStatus.OK
        assert response.data == {"rank": 1, "points": 0}
        self.client.force_authenticate(user=user2)
        response = self.client.get("/rank/")
        assert response.data == {"rank": 1, "points": 0}
        self.client.post(
            "/cloudflare-webhook/",
            data={
                "uid": "af95bfce3e887accd1fe9796f741b5f1",
                "creator": None,
                "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                "thumbnailTimestampPct": 0,
                "readyToStream": True,
                "readyToStreamAt": "2024-07-05T19:54:15.176348Z",
                "status": {
                    "state": "ready",
                    "step": "encoding",
                    "pctComplete": "66.000000",
                    "errorReasonCode": "",
                    "errorReasonText": "",
                },
                "meta": {
                    "firebase_uid": "0dSkRQUJmuUnf5mdDOUr7bxRP1a2",
                    "latitude": "51.512863471620285",
                    "longitude": "-0.03338590123538324",
                    "purpose": "Shopping",
                },
                "created": "2024-07-05T19:54:00.406659Z",
                "modified": "2024-07-05T19:54:15.175015Z",
                "scheduledDeletion": None,
                "size": 626012,
                "preview": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/watch",
                "allowedOrigins": [],
                "requireSignedURLs": False,
                "uploaded": "2024-07-05T19:54:00.406655Z",
                "uploadExpiry": "2024-07-06T19:53:59Z",
                "maxSizeBytes": None,
                "maxDurationSeconds": 30,
                "duration": 1,
                "input": {"width": 720, "height": 1280},
                "playback": {
                    "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8",
                    "dash": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.mpd",
                },
                "watermark": None,
                "clippedFrom": None,
                "publicDetails": None,
            },
            headers={
                "Webhook-Signature": "time=1720209265,sig1=651cc3328400b51eab2fa94a8ce6a02023493969907ff169bd2cc5ea79781b31"
            },
            format="json",
        )
        response = self.client.get("/rank/")
        assert response.data == {"rank": 1, "points": 10000}
        self.client.force_authenticate(user=user)
        response = self.client.get("/rank/")
        assert response.data == {"rank": 2, "points": 0}
