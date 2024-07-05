import hashlib
import hmac
import os

from rest_framework import permissions


class IsFromCloudflare(permissions.BasePermission):
    def has_permission(self, request, view):
        cloudflare_signature = request.META.get("HTTP_WEBHOOK_SIGNATURE")
        if not cloudflare_signature:
            return False
        cloudflare_signature = cloudflare_signature.split(",")
        timestamp = cloudflare_signature[0].split("=")[1]
        expected_signature = cloudflare_signature[1].split("=")[1]
        payload = bytes(timestamp, "UTF-8") + bytes(".", "UTF-8") + request.body

        digest = hmac.new(
            bytes(os.environ.get("CLOUDFLARE_WEBHOOK_SECRET", ""), "UTF-8"),
            payload,
            hashlib.sha256,
        )
        signature = digest.hexdigest()
        valid_signature = expected_signature == signature
        return valid_signature
