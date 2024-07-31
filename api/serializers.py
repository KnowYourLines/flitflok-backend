import base64
import datetime
import os

import requests
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from firebase_admin import auth
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from api.models import User, Video


class PlaybackIdSerializer(serializers.Serializer):
    id = serializers.CharField()


class PlaybackSerializer(serializers.Serializer):
    hls = serializers.URLField()


class MetaSerializer(serializers.Serializer):
    firebase_uid = serializers.CharField()
    latitude = serializers.CharField()
    longitude = serializers.CharField()


class WebhookEventSerializer(serializers.Serializer):
    readyToStream = serializers.BooleanField()
    readyToStreamAt = serializers.DateTimeField()
    playback = PlaybackSerializer()
    thumbnail = serializers.URLField()
    preview = serializers.URLField()
    uid = serializers.CharField()
    meta = MetaSerializer()

    def save(self):
        ready = self.validated_data["readyToStream"]
        if ready:
            creator = User.objects.get(
                username=self.validated_data["meta"]["firebase_uid"]
            )
            location = Point(
                float(self.validated_data["meta"]["longitude"]),
                float(self.validated_data["meta"]["latitude"]),
                srid=4326,
            )
            video, created = Video.objects.update_or_create(
                cloudflare_uid=self.validated_data["uid"],
                defaults={
                    "creator": creator,
                    "location": location,
                    "thumbnail": self.validated_data["thumbnail"],
                    "preview": self.validated_data["preview"],
                    "hls": f"{self.validated_data['playback']['hls']}?clientBandwidthHint=1000",
                    "uploaded_at": self.validated_data["readyToStreamAt"],
                },
            )
            if (
                created
                and not Video.objects.filter(location__distance_lte=(location, D(mi=1)))
                .exclude(id=video.id)
                .exists()
            ):
                creator.points += 1000
                creator.save()


class UserRankSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["rank", "points"]

    def get_rank(self, obj):
        user_points = obj.points
        num_users_ranked_above = User.objects.filter(points__gt=user_points).count()
        return num_users_ranked_above + 1


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["agreed_to_eula"]


class DisplayNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["display_name"]


class VideoUploadSerializer(serializers.Serializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    location = serializers.URLField(read_only=True)

    def create(self, validated_data):
        endpoint = f"https://api.cloudflare.com/client/v4/accounts/{os.environ.get('CLOUDFLARE_ACCOUNT_ID')}/stream?direct_user=true"
        max_duration = base64.b64encode(b"30").decode("utf-8")
        expiry = base64.b64encode(
            (datetime.datetime.utcnow() + datetime.timedelta(days=1))
            .strftime("%Y-%m-%dT%H:%M:%SZ")
            .encode()
        ).decode("utf-8")
        firebase_uid = base64.b64encode(
            self.context["request"].user.username.encode()
        ).decode("utf-8")
        headers = {
            "Authorization": f"bearer {os.environ.get('CLOUDFLARE_API_TOKEN')}",
            "Tus-Resumable": "1.0.0",
            "Upload-Length": self.context["request"].headers["Upload-Length"],
            "Upload-Metadata": f"maxDurationSeconds {max_duration}, expiry {expiry}, firebase_uid {firebase_uid}, "
            + self.context["request"].headers["Upload-Metadata"],
        }

        response = requests.request("POST", endpoint, headers=headers)
        return {
            "location": response.headers.get("Location"),
        }

    def validate(self, data):
        metadata = self.context["request"].headers["Upload-Metadata"]
        if "maxDurationSeconds" in metadata:
            raise serializers.ValidationError(
                "Max upload duration cannot be user defined"
            )
        if "expiry" in metadata:
            raise serializers.ValidationError("Upload expiry cannot be user defined")
        if int(self.context["request"].headers["Upload-Length"]) < 1:
            raise serializers.ValidationError(
                "Upload length must be a positive integer"
            )
        return data

    def validate_creator(self, creator):
        user = auth.get_user(creator.username)
        if not user.email_verified:
            raise serializers.ValidationError("Verified email address required")
        return creator


class VideoBlockSerializer(serializers.Serializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_creator(self, value):
        if self.instance.creator == value:
            raise serializers.ValidationError("You cannot block yourself")
        return value

    def update(self, instance, validated_data):
        user = validated_data.get("creator")
        user.blocked_users.add(instance.creator)
        user.save()
        return instance


class VideoHideSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        user = self.context["request"].user
        instance.hidden_from.add(user)
        instance.save()
        return instance


class VideoWentSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        user = self.context["request"].user
        if (
            not instance.directions_requested_by.filter(username=user.username).exists()
            and instance.creator != user
        ):
            num_creators_around = 1 + (
                Video.objects.filter(
                    location__distance_lte=(instance.location, D(mi=1))
                )
                .exclude(creator=instance.creator)
                .order_by("creator")
                .distinct("creator")
                .count()
            )
            creator = instance.creator
            creator.points += 10 * num_creators_around
            creator.save()
        instance.directions_requested_by.add(user)
        instance.save()
        return instance


class VideoReportSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        user = self.context["request"].user
        instance.reported_by.add(user)
        instance.save()
        context = {"reported_video_id": str(instance.id)}
        html_message = render_to_string("reported_video.html", context=context)
        plain_message = strip_tags(html_message)

        message = EmailMultiAlternatives(
            subject=f"Video reported",
            from_email=f"FlitFlok <{os.environ.get('EMAIL_HOST_USER')}>",
            body=plain_message,
            to=[os.environ.get("EMAIL_HOST_USER")],
        )

        message.attach_alternative(html_message, "text/html")
        message.send()
        return instance


class VideoQueryParamSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    current_video = serializers.UUIDField(required=False)

    def validate_current_video(self, value):
        if not Video.objects.filter(id=value).exists():
            raise serializers.ValidationError("Current video does not exist")
        return value


class VideoResultsSerializer(GeoFeatureModelSerializer):
    distance = serializers.SerializerMethodField()
    posted_at = serializers.SerializerMethodField()
    creator_rank = serializers.SerializerMethodField()
    creator = serializers.ReadOnlyField(source="creator.username")
    display_name = serializers.ReadOnlyField(source="creator.display_name")

    class Meta:
        model = Video
        geo_field = "location"
        fields = (
            "id",
            "distance",
            "posted_at",
            "creator",
            "creator_rank",
            "display_name",
            "thumbnail",
            "hls",
        )

    def get_posted_at(self, obj):
        return obj.uploaded_at.timestamp()

    def get_distance(self, obj):
        return f"{round(obj.distance.km, 1)} km"

    def get_creator_rank(self, obj):
        user_points = obj.creator.points
        num_users_ranked_above = User.objects.filter(points__gt=user_points).count()
        return num_users_ranked_above + 1


class VideosBlockedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ("id",)

    def to_representation(self, instance):
        video = super().to_representation(instance)
        return video["id"]
