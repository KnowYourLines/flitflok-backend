import os

import requests
from firebase_admin import auth
from rest_framework.test import APITestCase

from api.models import User, Video
from http import HTTPStatus


class VideoUploadTest(APITestCase):
    def test_gets_upload_response(self):
        user = User.objects.create(username="zVAvUkRbSbgZCSnZ64hU9PyutCi1")
        self.client.force_authenticate(user=user)
        response = self.client.post(
            "/video-upload/",
            headers={
                "Upload-Length": "1690691",
                "Upload-Metadata": "purpose dGVzdA==,latitude NTEuNTEyODg4MzI2OTk3Njk=,longitude LTAuMDMzMzg5MTUzNzQwNzMyNjA1",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert not response.data
        assert response.headers["Access-Control-Allow-Headers"] == "*"
        assert response.headers["Access-Control-Allow-Origin"] == "*"
        assert response.headers["Access-Control-Expose-Headers"] == "Location"
        assert response.headers["Location"].startswith(
            "https://upload.videodelivery.net/tus/"
        )
        url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ.get('CLOUDFLARE_ACCOUNT_ID')}/stream?purpose=test"
        headers = {
            "Authorization": f"bearer {os.environ.get('CLOUDFLARE_API_TOKEN')}",
        }
        response = requests.request("GET", url, headers=headers)
        videos = response.json()["result"]
        for video in videos:
            url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ.get('CLOUDFLARE_ACCOUNT_ID')}/stream/{video['uid']}"
            requests.request("DELETE", url, headers=headers)

    def test_must_be_verified_to_upload(self):
        firebase_user = auth.create_user()
        uid = firebase_user.uid
        user = User.objects.create(username=uid)
        self.client.force_authenticate(user=user)
        response = self.client.post(
            "/video-upload/",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data["creator"][0] == "Verified email address required"
        auth.delete_user(uid)

    def test_upload_length_must_be_positive_integer(self):
        user = User.objects.create(username="zVAvUkRbSbgZCSnZ64hU9PyutCi1")
        self.client.force_authenticate(user=user)
        response = self.client.post(
            "/video-upload/",
            headers={
                "Upload-Length": "-34534534",
                "Upload-Metadata": "purpose Rm9vZCAmIERyaW5r,latitude NTEuNTEyODg4MzI2OTk3Njk=,longitude LTAuMDMzMzg5MTUzNzQwNzMyNjA1",
            },
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data[0] == "Upload length must be a positive integer"

    def test_upload_metadata_cannot_define_max_duration(self):
        user = User.objects.create(username="zVAvUkRbSbgZCSnZ64hU9PyutCi1")
        self.client.force_authenticate(user=user)
        response = self.client.post(
            "/video-upload/",
            headers={
                "Upload-Length": "34534534",
                "Upload-Metadata": "maxDurationSeconds NTEuNTEyODg4MzI2OTk3Njk=,longitude LTAuMDMzMzg5MTUzNzQwNzMyNjA1",
            },
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data[0] == "Max upload duration cannot be user defined"

    def test_upload_metadata_cannot_define_expiry(self):
        user = User.objects.create(username="zVAvUkRbSbgZCSnZ64hU9PyutCi1")
        self.client.force_authenticate(user=user)
        response = self.client.post(
            "/video-upload/",
            headers={
                "Upload-Length": "34534534",
                "Upload-Metadata": "expiry NTEuNTEyODg4MzI2OTk3Njk=,longitude LTAuMDMzMzg5MTUzNzQwNzMyNjA1",
            },
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data[0] == "Upload expiry cannot be user defined"
