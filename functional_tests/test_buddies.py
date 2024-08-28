from http import HTTPStatus

from rest_framework.test import APITestCase

from api.models import User


class BuddiesTest(APITestCase):
    def test_retrieves_buddies(self):
        user = User.objects.create(username="hello")
        buddy = User.objects.create(username="world")
        user.buddies.add(buddy)
        self.client.force_authenticate(user=user)
        response = self.client.get(
            f"/buddies/",
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == [{"display_name": None, "username": "world"}]

    def test_removes_buddies(self):
        user = User.objects.create(username="hello")
        buddy = User.objects.create(username="world")
        user.buddies.add(buddy)
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            f"/buddies/{buddy.username}/remove/",
        )
        assert response.status_code == HTTPStatus.NO_CONTENT
        assert not user.buddies.all()

    def test_can_only_remove_if_buddy(self):
        user = User.objects.create(username="hello")
        buddy = User.objects.create(username="world")
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            f"/buddies/{buddy.username}/remove/",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data[0] == "User is not your buddy"

    def test_blocks_buddies(self):
        user = User.objects.create(username="hello")
        buddy = User.objects.create(username="world")
        user.buddies.add(buddy)
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            f"/buddies/{buddy.username}/block/",
        )
        assert response.status_code == HTTPStatus.NO_CONTENT
        assert not user.buddies.all()
        assert user.blocked_users.filter(username=buddy.username).exists()

    def test_can_only_block_if_buddy(self):
        user = User.objects.create(username="hello")
        buddy = User.objects.create(username="world")
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            f"/buddies/{buddy.username}/block/",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data[0] == "User is not your buddy"
