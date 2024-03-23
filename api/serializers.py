from firebase_admin import storage
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from api.models import User, Video


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["agreed_to_eula"]


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


class VideoUpdateSerializer(serializers.Serializer):
    reported = serializers.BooleanField(required=False)
    hidden = serializers.BooleanField(required=False)

    def validate(self, data):
        if not data.get("reported") and not data.get("hidden"):
            raise serializers.ValidationError(
                "Video must be either reported or hidden."
            )
        if data.get("reported") and data.get("hidden"):
            raise serializers.ValidationError(
                "Video must be either reported or hidden."
            )
        return data

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if validated_data.get("reported"):
            instance.reported_by.add(user)
        if validated_data.get("hidden"):
            instance.hidden_from.add(user)
        instance.save()
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
        )

    def get_posted_at(self, obj):
        return obj.posted_at

    def get_distance(self, obj):
        return obj.distance.km
