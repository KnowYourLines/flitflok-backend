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

    def test_sends_request_via_username(self):
        sender = User.objects.create(username="hello")
        receiver = User.objects.create(username="world", display_name="hello world")
        self.client.force_authenticate(user=sender)
        response = self.client.post(
            f"/buddy-request/",
            data={"display_name": receiver.username},
            format="json",
        )
        assert response.status_code == HTTPStatus.CREATED
        assert BuddyRequest.objects.filter(sender=sender, receiver=receiver).exists()

    def test_cannot_duplicate_request(self):
        sender = User.objects.create(username="hello")
        receiver = User.objects.create(username="world", display_name="hello world")
        BuddyRequest.objects.create(sender=sender, receiver=receiver)
        self.client.force_authenticate(user=sender)
        response = self.client.post(
            f"/buddy-request/",
            data={"display_name": receiver.display_name},
            format="json",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data["display_name"][0] == "Request already sent"

    def test_receiver_must_exist(self):
        sender = User.objects.create(username="hello")
        receiver = User.objects.create(username="world", display_name="hello world")
        BuddyRequest.objects.create(sender=sender, receiver=receiver)
        self.client.force_authenticate(user=sender)
        response = self.client.post(
            f"/buddy-request/",
            data={"display_name": "goodbye"},
            format="json",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data["display_name"][0] == "User does not exist"

    def test_accepts_request(self):
        sender = User.objects.create(username="hello")
        receiver = User.objects.create(username="world", display_name="hello world")
        buddy_request = BuddyRequest.objects.create(sender=sender, receiver=receiver)
        self.client.force_authenticate(user=receiver)
        response = self.client.patch(
            f"/buddy-request/{buddy_request.id}/accept/",
        )
        assert response.status_code == HTTPStatus.ACCEPTED
        assert sender.buddies.filter(username=receiver.username).exists()
        assert receiver.buddies.filter(username=sender.username).exists()

    def test_only_receiver_can_accept_request(self):
        sender = User.objects.create(username="hello")
        receiver = User.objects.create(username="world", display_name="hello world")
        buddy_request = BuddyRequest.objects.create(sender=sender, receiver=receiver)
        self.client.force_authenticate(user=sender)
        response = self.client.patch(
            f"/buddy-request/{buddy_request.id}/accept/",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data[0] == "Only the request receiver can accept"
