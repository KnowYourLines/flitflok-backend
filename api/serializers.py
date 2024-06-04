import os

from django.contrib.gis.measure import D
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from firebase_admin import storage
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from api.models import User, Video


class UserRankSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["rank"]

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


class VideoSerializer(GeoFeatureModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Video
        geo_field = "location"
        fields = ("creator", "place_name", "address", "file_id")

    def validate_file_id(self, value):
        bucket = storage.bucket()
        blob = bucket.blob(str(value))
        if not blob.exists():
            raise serializers.ValidationError("File does not exist")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        new_location = validated_data["location"]
        if not Video.objects.filter(
            location__distance_lte=(new_location, D(mi=1))
        ).exists():
            user.points += 10000
            user.save()
        return super().create(validated_data)


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
            num_unique_creator_videos_around = 1 + (
                Video.objects.filter(
                    location__distance_lte=(instance.location, D(mi=1))
                )
                .exclude(creator=instance.creator)
                .count()
            )
            creator = instance.creator
            creator.points += 10 * num_unique_creator_videos_around
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
            "place_name",
            "address",
            "file_id",
            "distance",
            "posted_at",
            "creator",
            "creator_rank",
            "display_name",
        )

    def get_posted_at(self, obj):
        return obj.created_at.timestamp()

    def get_distance(self, obj):
        return f"{round(obj.distance.km, 1)} km"

    def get_creator_rank(self, obj):
        return obj.creator_rank


class VideosBlockedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ("id",)

    def to_representation(self, instance):
        video = super().to_representation(instance)
        return video["id"]
