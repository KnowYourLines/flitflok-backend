import logging

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import Count, F, Window
from django.db.models.functions import DenseRank
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
    VideosBlockedSerializer,
    VideoWentSerializer,
    UserRankSerializer,
    DisplayNameSerializer,
    VideoUploadSerializer,
)


class VideoUploadView(APIView):
    def get(self, request):
        serializer = VideoUploadSerializer(
            data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DisplayNameView(APIView):
    def get(self, request):
        serializer = DisplayNameSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = DisplayNameSerializer(
            request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RankView(APIView):
    def get(self, request):
        serializer = UserRankSerializer(request.user)
        return Response(serializer.data)


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


class VideoWentView(APIView):
    def patch(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        serializer = VideoWentSerializer(
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
        video = serializer.save()
        blocked_videos = VideosBlockedSerializer(
            video.creator.video_set.all().order_by("-created_at"), many=True
        )
        return Response(blocked_videos.data, status=status.HTTP_200_OK)


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
            .annotate(number_directions_requests=Count("directions_requested_by"))
            .annotate(
                creator_rank=Window(
                    expression=DenseRank(),
                    order_by=F("creator__points").desc(),
                )
            )
        )
        if current_video_id := params.validated_data.get("current_video"):
            current_video = Video.objects.get(id=current_video_id)
            videos = videos.filter(
                distance__gt=Distance(
                    current_video.location, current_location, spheroid=True
                )
            )
        videos = videos.order_by(
            "distance",
            "-creator__points",
            "-created_at",
        )[:5]
        results = VideoResultsSerializer(videos, many=True)
        return Response(results.data, status=status.HTTP_200_OK)
