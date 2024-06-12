from unittest.mock import patch

from freezegun import freeze_time
from rest_framework.test import APITestCase

from http import HTTPStatus

from api.models import User, Video
from api.permissions import IsFromMux


class MuxWebhookTest(APITestCase):
    def test_requires_valid_header(self):
        with freeze_time("2024-06-10 22:24:02"):
            response = self.client.post(
                "/mux-webhook/",
                {
                    "type": "video.upload.asset_created",
                    "request_id": None,
                    "object": {
                        "type": "upload",
                        "id": "602229EJsGGo8epvgmH8qMsAjDLammVK4CgHnP8Pnvpo",
                    },
                    "id": "0ef554a6-b138-1484-2713-809fee24a001",
                    "environment": {"name": "Production", "id": "55g0gl"},
                    "data": {
                        "timeout": 3600,
                        "status": "asset_created",
                        "new_asset_settings": {
                            "playback_policies": ["public"],
                            "passthrough": "hello world",
                            "max_resolution_tier": "1080p",
                            "encoding_tier": "baseline",
                        },
                        "id": "602229EJsGGo8epvgmH8qMsAjDLammVK4CgHnP8Pnvpo",
                        "cors_origin": "*",
                        "asset_id": "nIBvNd01huS4qQFB7tL76L2xALOc01nzH4TQsUmV8n7ys",
                    },
                    "created_at": "2024-06-10T22:24:01.561000Z",
                    "attempts": [],
                    "accessor_source": None,
                    "accessor": None,
                },
                format="json",
                headers={
                    "Mux-Signature": "t=1718058242,v1=d6a4b3e3a83320b9af87d8717e2cf0700ec246416750c2ac27e5bc0987b19cf6"
                },
            )
        assert response.status_code == HTTPStatus.OK

    @patch.object(IsFromMux, "has_permission")
    def test_saves_asset_info(self, mock_has_permission):
        user = User.objects.create()
        video = Video.objects.create(creator=user)
        mock_has_permission.return_value = True
        response = self.client.post(
            "/mux-webhook/",
            {
                "type": "video.asset.ready",
                "request_id": None,
                "object": {
                    "type": "asset",
                    "id": "d67h5rEZl02A5302VZ2Sx01frHf1tuJoDvbuuPNb8Gjza8",
                },
                "id": "ba071cd9-725f-9d31-fe24-2d3965c9387e",
                "environment": {"name": "Production", "id": "55g0gl"},
                "data": {
                    "upload_id": "UgDk8NMzRVkm56PG6qJ12YepMMbRNl7G4qY8u00X3Ths",
                    "tracks": [
                        {
                            "type": "video",
                            "max_width": 1080,
                            "max_height": 1920,
                            "max_frame_rate": 29.925,
                            "id": "KgoatJIuRS02017InREUyn00cwPm02m5I7EILKJxhYGJzRA",
                            "duration": 0.666667,
                        },
                        {
                            "type": "audio",
                            "status": "ready",
                            "primary": True,
                            "name": "Default",
                            "max_channels": 1,
                            "language_code": "und",
                            "id": "Bn1OPQX02FQt6psksgcTi01xVQCUIMNB1MXIbloHjfKflVG6M00BbTriQ",
                        },
                    ],
                    "status": "ready",
                    "resolution_tier": "1080p",
                    "playback_ids": [
                        {
                            "policy": "public",
                            "id": "9P57BUhqIjJNi4RKPR02XVZmAYSSjuj6tVOK6DDe7MgM",
                        }
                    ],
                    "passthrough": str(video.id),
                    "non_standard_input_reasons": {"video_codec": "hevc"},
                    "mp4_support": "none",
                    "max_stored_resolution": "HD",
                    "max_stored_frame_rate": 29.925,
                    "max_resolution_tier": "1080p",
                    "master_access": "none",
                    "ingest_type": "on_demand_direct_upload",
                    "id": "d67h5rEZl02A5302VZ2Sx01frHf1tuJoDvbuuPNb8Gjza8",
                    "encoding_tier": "baseline",
                    "duration": 0.649556,
                    "created_at": 1718058159,
                    "aspect_ratio": "9:16",
                },
                "created_at": "2024-06-10T22:22:41.488000Z",
                "attempts": [
                    {
                        "webhook_id": 44699,
                        "response_status_code": 403,
                        "response_headers": {
                            "x-frame-options": "DENY",
                            "x-content-type-options": "nosniff",
                            "vary": "Accept",
                            "server": "gunicorn",
                            "referrer-policy": "same-origin",
                            "date": "Mon, 10 Jun 2024 22:22:42 GMT",
                            "cross-origin-opener-policy": "same-origin",
                            "content-type": "application/json",
                            "content-length": "63",
                            "allow": "POST, OPTIONS",
                        },
                        "response_body": '{"detail":"You do not have permission to perform this action."}',
                        "max_attempts": 30,
                        "id": "c88d3d1c-daef-484e-8214-ee7c8924f32d",
                        "created_at": "2024-06-10T22:22:42.000000Z",
                        "address": "https://tender-amoeba-neatly.ngrok-free.app/mux-webhook/",
                    }
                ],
                "accessor_source": None,
                "accessor": None,
            },
            format="json",
            headers={
                "Mux-Signature": "t=1718058242,v1=d6a4b3e3a83320b9af87d8717e2cf0700ec246416750c2ac27e5bc0987b19cf6"
            },
        )
        assert response.status_code == HTTPStatus.OK
        video = Video.objects.get(id=video.id)
        assert video.playback_id == "9P57BUhqIjJNi4RKPR02XVZmAYSSjuj6tVOK6DDe7MgM"
        assert video.asset_id == "d67h5rEZl02A5302VZ2Sx01frHf1tuJoDvbuuPNb8Gjza8"
