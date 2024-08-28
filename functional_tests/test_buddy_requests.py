from http import HTTPStatus

from rest_framework.test import APITestCase

from api.models import User, BuddyRequest


class BuddyRequestsTest(APITestCase):
    def test_sends_buddy_request(self):
        sender = User.objects.create(username="hello")
        receiver = User.objects.create(username="world", display_name="hello world")
        self.client.force_authenticate(user=sender)
        response = self.client.post(
            f"/buddy-request/",
            data={"display_name": receiver.display_name},
            format="json",
        )
        assert response.status_code == HTTPStatus.CREATED
        assert BuddyRequest.objects.filter(sender=sender, receiver=receiver).exists()
