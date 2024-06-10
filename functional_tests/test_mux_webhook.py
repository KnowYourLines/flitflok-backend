from freezegun import freeze_time
from rest_framework.test import APITestCase

from http import HTTPStatus


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
