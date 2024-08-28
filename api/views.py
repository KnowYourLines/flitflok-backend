import logging

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from firebase_admin.auth import delete_user
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Video, User, BuddyRequest
from api.permissions import IsFromCloudflare
from api.serializers import (
    UserSerializer,
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
    WebhookEventSerializer,
    BuddyRequestSerializer,
    AcceptBuddyRequestSerializer,
    DeclineBuddyRequestSerializer,
    BlockBuddyRequestSerializer,
    SentBuddyRequestsSerializer,
)

logger = logging.getLogger(__name__)


class SentBuddyRequestsView(APIView):
    def get(self, request):
        serializer = SentBuddyRequestsSerializer(
            BuddyRequest.objects.filter(sender=request.user), many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class BuddyRequestView(APIView):
    def post(self, request):
        serializer = BuddyRequestSerializer(
            data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


class BlockBuddyRequestView(APIView):
    def patch(self, request, pk):
        buddy_request = get_object_or_404(BuddyRequest, pk=pk)
        serializer = BlockBuddyRequestSerializer(
            buddy_request, data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeclineBuddyRequestView(APIView):
    def delete(self, request, pk):
        buddy_request = get_object_or_404(BuddyRequest, pk=pk)
        serializer = DeclineBuddyRequestSerializer(
            buddy_request, data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AcceptBuddyRequestView(APIView):
    def patch(self, request, pk):
        buddy_request = get_object_or_404(BuddyRequest, pk=pk)
        serializer = AcceptBuddyRequestSerializer(
            buddy_request, data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)


class CloudflareWebhookView(APIView):
    authentication_classes = []
    permission_classes = [IsFromCloudflare]

    def post(self, request):
        serializer = WebhookEventSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class VideoUploadView(APIView):
    def post(self, request):
        serializer = VideoUploadSerializer(
            data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            None,
            headers={
                "Access-Control-Expose-Headers": "Location",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*",
                "Location": serializer.data["location"],
            },
        )


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
        user = User.objects.get(username=request.user.username)
        serializer = UserRankSerializer(user)
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
            video.creator.video_set.all().order_by("-uploaded_at"), many=True
        )
        return Response(blocked_videos.data, status=status.HTTP_200_OK)


class VideoView(APIView):
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
            "-uploaded_at",
        )[:5]
        results = VideoResultsSerializer(videos, many=True)
        return Response(results.data, status=status.HTTP_200_OK)
