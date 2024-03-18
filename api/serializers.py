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


class VideoQueryParamSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    current_video = serializers.UUIDField(required=False)


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
