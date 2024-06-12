import datetime
import hashlib
import hmac
import os

from rest_framework import permissions


class IsFromMux(permissions.BasePermission):
    def has_permission(self, request, view):
        mux_signature = request.META.get("HTTP_MUX_SIGNATURE")
        if not mux_signature:
            return False
        mux_signature = mux_signature.split(",")
        timestamp = mux_signature[0].split("=")[1]
        expected_signature = mux_signature[1].split("=")[1]
        payload = bytes(timestamp, "UTF-8") + bytes(".", "UTF-8") + request.body

        digest = hmac.new(
            bytes(os.environ.get("MUX_SIGNING_SECRET", ""), "UTF-8"),
            payload,
            hashlib.sha256,
        )
        signature = digest.hexdigest()
        valid_signature = expected_signature == signature
        valid_timestamp = (
            datetime.datetime.now() - datetime.datetime.fromtimestamp(int(timestamp))
        ).total_seconds() <= 300
        return valid_signature and valid_timestamp


class IsVideoCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user
