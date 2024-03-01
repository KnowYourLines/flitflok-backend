from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import EulaAgreedSerializer, UserSerializer


class EulaAgreedView(APIView):
    def get(self, request):
        output = UserSerializer(request.user).data
        return Response(output)

    def patch(self, request):
        serializer = EulaAgreedSerializer(
            request.user,
            data=request.data,
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            output = UserSerializer(request.user).data
            return Response(output)
