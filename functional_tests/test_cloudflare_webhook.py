import decimal

from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase

from http import HTTPStatus

from api.models import User, Video


class CloudflareWebhookTest(APITestCase):
    def test_creates_new_video(self):
        creator = User.objects.create(username="0dSkRQUJmuUnf5mdDOUr7bxRP1a2")
        starring = User.objects.create(username="hello world")
        response = self.client.post(
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
                    "starring_firebase_uid": "hello world",
                    "latitude": "51.512863471620285",
                    "longitude": "-0.03338590123538324",
                    "currency": "GBP",
                    "money_spent": "5.67",
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
                "Webhook-Signature": "time=1720209265,sig1=4bda2ef941443b7a77de219db12cc49657fb6c67db1b15d80edc32385e73f775"
            },
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        video = Video.objects.get(cloudflare_uid="af95bfce3e887accd1fe9796f741b5f1")
        assert (
            video.hls
            == "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=10"
        )
        assert (
            video.thumbnail
            == "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg"
        )
        assert (
            video.preview
            == "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/watch"
        )
        assert video.creator == creator
        assert video.location == Point(
            -0.03338590123538324,
            51.512863471620285,
            srid=4326,
        )
        assert str(video.uploaded_at) == "2024-07-05 19:54:15.176348+00:00"
        assert video.money_spent == decimal.Decimal("5.67")
        assert video.currency == "GBP"
        assert video.starring == starring
