import datetime
import uuid
from http import HTTPStatus
from unittest.mock import patch

from rest_framework.test import APITestCase

from api.models import User, Video
from api.permissions import IsFromCloudflare


class VideoResultsTest(APITestCase):
    @patch.object(IsFromCloudflare, "has_permission")
    def test_orders_by_distance_creator_points_timestamp(self, mock_has_permission):
        mock_has_permission.return_value = True
        user = User.objects.create(username="hello world")
        self.client.post(
            "/cloudflare-webhook/",
            data={
                "uid": "af95bfce3e887accd1fe9796f741b5f1",
                "creator": None,
                "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                "thumbnailTimestampPct": 0,
                "readyToStream": True,
                "readyToStreamAt": datetime.datetime(
                    2012, 1, 14, tzinfo=datetime.timezone.utc
                ),
                "status": {
                    "state": "ready",
                    "step": "encoding",
                    "pctComplete": "66.000000",
                    "errorReasonCode": "",
                    "errorReasonText": "",
                },
                "meta": {
                    "firebase_uid": user.username,
                    "latitude": "51.51291201050047",
                    "longitude": "-0.0333876462451904",
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
        self.client.post(
            "/cloudflare-webhook/",
            data={
                "uid": "bf95bfce3e887accd1fe9796f741b5f1",
                "creator": None,
                "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                "thumbnailTimestampPct": 0,
                "readyToStream": True,
                "readyToStreamAt": datetime.datetime(
                    2012, 1, 14, tzinfo=datetime.timezone.utc
                ),
                "status": {
                    "state": "ready",
                    "step": "encoding",
                    "pctComplete": "66.000000",
                    "errorReasonCode": "",
                    "errorReasonText": "",
                },
                "meta": {
                    "firebase_uid": user.username,
                    "latitude": "51.491857",
                    "longitude": "-0.011591",
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
        User.objects.create(username="best explorer", points=1000000000000000)
        user2 = User.objects.create(username="goodbye world")
        self.client.post(
            "/cloudflare-webhook/",
            data={
                "uid": "cf95bfce3e887accd1fe9796f741b5f1",
                "creator": None,
                "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                "thumbnailTimestampPct": 0,
                "readyToStream": True,
                "readyToStreamAt": datetime.datetime(
                    2023, 1, 14, tzinfo=datetime.timezone.utc
                ),
                "status": {
                    "state": "ready",
                    "step": "encoding",
                    "pctComplete": "66.000000",
                    "errorReasonCode": "",
                    "errorReasonText": "",
                },
                "meta": {
                    "firebase_uid": user2.username,
                    "latitude": "51.491857",
                    "longitude": "-0.011591",
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
        self.client.force_authenticate(user=user)
        self.client.post(
            "/cloudflare-webhook/",
            data={
                "uid": "df95bfce3e887accd1fe9796f741b5f1",
                "creator": None,
                "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                "thumbnailTimestampPct": 0,
                "readyToStream": True,
                "readyToStreamAt": datetime.datetime(
                    2023, 1, 14, tzinfo=datetime.timezone.utc
                ),
                "status": {
                    "state": "ready",
                    "step": "encoding",
                    "pctComplete": "66.000000",
                    "errorReasonCode": "",
                    "errorReasonText": "",
                },
                "meta": {
                    "firebase_uid": user.username,
                    "latitude": "51.491857",
                    "longitude": "-0.011591",
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
        current_latitude = 51.51291201050047
        current_longitude = -0.0333876462451904
        response = self.client.get(
            f"/video/?latitude={current_latitude}&longitude={current_longitude}"
        )
        assert response.data == {
            "type": "FeatureCollection",
            "features": [
                {
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="af95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.03338764624519, 51.51291201050047],
                    },
                    "properties": {
                        "distance": "0.0 km",
                        "posted_at": datetime.datetime(
                            2012, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 2,
                        "display_name": None,
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="df95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                    "properties": {
                        "distance": "2.8 km",
                        "posted_at": datetime.datetime(
                            2023, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 2,
                        "display_name": None,
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="bf95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                    "properties": {
                        "distance": "2.8 km",
                        "posted_at": datetime.datetime(
                            2012, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 2,
                        "display_name": None,
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="cf95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                    "properties": {
                        "distance": "2.8 km",
                        "posted_at": datetime.datetime(
                            2023, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "goodbye world",
                        "creator_rank": 3,
                        "display_name": None,
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                    },
                },
            ],
        }

    @patch.object(IsFromCloudflare, "has_permission")
    def test_finds_next_5_videos(self, mock_has_permission):
        mock_has_permission.return_value = True
        user = User.objects.create(username="hello world")
        self.client.force_authenticate(user=user)
        self.client.post(
            "/cloudflare-webhook/",
            data={
                "uid": "af95bfce3e887accd1fe9796f741b5f1",
                "creator": None,
                "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                "thumbnailTimestampPct": 0,
                "readyToStream": True,
                "readyToStreamAt": datetime.datetime(
                    2012, 1, 14, tzinfo=datetime.timezone.utc
                ),
                "status": {
                    "state": "ready",
                    "step": "encoding",
                    "pctComplete": "66.000000",
                    "errorReasonCode": "",
                    "errorReasonText": "",
                },
                "meta": {
                    "firebase_uid": user.username,
                    "latitude": "51.51291201050047",
                    "longitude": "-0.0333876462451904",
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
        self.client.post(
            "/cloudflare-webhook/",
            data={
                "uid": "bf95bfce3e887accd1fe9796f741b5f1",
                "creator": None,
                "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                "thumbnailTimestampPct": 0,
                "readyToStream": True,
                "readyToStreamAt": datetime.datetime(
                    2022, 1, 14, tzinfo=datetime.timezone.utc
                ),
                "status": {
                    "state": "ready",
                    "step": "encoding",
                    "pctComplete": "66.000000",
                    "errorReasonCode": "",
                    "errorReasonText": "",
                },
                "meta": {
                    "firebase_uid": user.username,
                    "latitude": "51.491857",
                    "longitude": "-0.011591",
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
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="af95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.03338764624519, 51.51291201050047],
                    },
                    "properties": {
                        "distance": "0.0 km",
                        "posted_at": datetime.datetime(
                            2012, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="bf95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                    "properties": {
                        "distance": "2.8 km",
                        "posted_at": datetime.datetime(
                            2022, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
                    },
                },
            ],
        }
        self.client.post(
            "/cloudflare-webhook/",
            data={
                "uid": "cf95bfce3e887accd1fe9796f741b5f1",
                "creator": None,
                "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                "thumbnailTimestampPct": 0,
                "readyToStream": True,
                "readyToStreamAt": datetime.datetime(
                    2022, 1, 14, tzinfo=datetime.timezone.utc
                ),
                "status": {
                    "state": "ready",
                    "step": "encoding",
                    "pctComplete": "66.000000",
                    "errorReasonCode": "",
                    "errorReasonText": "",
                },
                "meta": {
                    "firebase_uid": user.username,
                    "latitude": "53.767750",
                    "longitude": "-0.335827",
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
        self.client.post(
            "/cloudflare-webhook/",
            data={
                "uid": "df95bfce3e887accd1fe9796f741b5f1",
                "creator": None,
                "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                "thumbnailTimestampPct": 0,
                "readyToStream": True,
                "readyToStreamAt": datetime.datetime(
                    2022, 2, 14, tzinfo=datetime.timezone.utc
                ),
                "status": {
                    "state": "ready",
                    "step": "encoding",
                    "pctComplete": "66.000000",
                    "errorReasonCode": "",
                    "errorReasonText": "",
                },
                "meta": {
                    "firebase_uid": user.username,
                    "latitude": "55.953251",
                    "longitude": "-3.188267",
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
        self.client.post(
            "/cloudflare-webhook/",
            data={
                "uid": "ef95bfce3e887accd1fe9796f741b5f1",
                "creator": None,
                "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                "thumbnailTimestampPct": 0,
                "readyToStream": True,
                "readyToStreamAt": datetime.datetime(
                    2022, 1, 15, tzinfo=datetime.timezone.utc
                ),
                "status": {
                    "state": "ready",
                    "step": "encoding",
                    "pctComplete": "66.000000",
                    "errorReasonCode": "",
                    "errorReasonText": "",
                },
                "meta": {
                    "firebase_uid": user.username,
                    "latitude": "53.767750",
                    "longitude": "-0.335827",
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
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="ef95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                    "properties": {
                        "distance": "251.8 km",
                        "posted_at": datetime.datetime(
                            2022, 1, 15, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
                    },
                },
                {
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="cf95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                    "properties": {
                        "distance": "251.8 km",
                        "posted_at": datetime.datetime(
                            2022, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="df95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-3.188267, 55.953251],
                    },
                    "properties": {
                        "distance": "536.1 km",
                        "posted_at": datetime.datetime(
                            2022, 2, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
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
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="af95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.03338764624519, 51.51291201050047],
                    },
                    "properties": {
                        "distance": "0.0 km",
                        "posted_at": datetime.datetime(
                            2012, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="bf95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.011591, 51.491857],
                    },
                    "properties": {
                        "distance": "2.8 km",
                        "posted_at": datetime.datetime(
                            2022, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="ef95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                    "properties": {
                        "distance": "251.8 km",
                        "posted_at": datetime.datetime(
                            2022, 1, 15, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
                    },
                },
                {
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="cf95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-0.335827, 53.767750],
                    },
                    "properties": {
                        "distance": "251.8 km",
                        "posted_at": datetime.datetime(
                            2022, 1, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
                    },
                },
                {
                    "type": "Feature",
                    "id": str(
                        Video.objects.get(
                            cloudflare_uid="df95bfce3e887accd1fe9796f741b5f1"
                        ).id
                    ),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-3.188267, 55.953251],
                    },
                    "properties": {
                        "distance": "536.1 km",
                        "posted_at": datetime.datetime(
                            2022, 2, 14, 0, 0, tzinfo=datetime.timezone.utc
                        ).timestamp(),
                        "creator": "hello world",
                        "creator_rank": 1,
                        "display_name": None,
                        "thumbnail": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/thumbnails/thumbnail.jpg",
                        "hls": "https://customer-ar0494u0olvml2w7.cloudflarestream.com/af95bfce3e887accd1fe9796f741b5f1/manifest/video.m3u8?clientBandwidthHint=1000",
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
