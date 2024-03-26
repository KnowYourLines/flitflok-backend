from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models.functions import TruncMinute
from firebase_admin.auth import delete_user
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Video
from api.serializers import (
    UserSerializer,
    VideoSerializer,
    VideoQueryParamSerializer,
    VideoResultsSerializer,
    VideoHideSerializer,
    VideoReportSerializer,
    VideoBlockSerializer,
)


class EulaAgreedView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DeleteAccountView(APIView):
    def delete(self, request):
        delete_user(request.user.username)
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VideoReportView(APIView):
    def patch(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        serializer = VideoReportSerializer(
            video, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VideoHideView(APIView):
    def patch(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        serializer = VideoHideSerializer(
            video, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VideoBlockView(APIView):
    def patch(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        serializer = VideoBlockSerializer(
            video, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VideoView(APIView):
    def post(self, request):
        serializer = VideoSerializer(
            data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        params = VideoQueryParamSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        latitude = params.validated_data["latitude"]
        longitude = params.validated_data["longitude"]
        current_location = Point(longitude, latitude, srid=4326)
        videos = (
            Video.objects.exclude(reported_by=self.request.user)
            .exclude(hidden_from=self.request.user)
            .exclude(creator__in=self.request.user.blocked_users.all())
            .annotate(distance=Distance("location", current_location, spheroid=True))
            .annotate(posted_at=TruncMinute("created_at"))
        ).order_by("distance", "-created_at")
        if current_video := params.validated_data.get("current_video"):
            current_index = next(
                index for index, video in enumerate(videos) if video.id == current_video
            )
            videos = videos[current_index + 1 : current_index + 3]
        else:
            videos = videos[:2]
        results = VideoResultsSerializer(videos, many=True)
        return Response(results.data, status=status.HTTP_200_OK)
