from firebase_admin.auth import delete_user
from rest_framework import status
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


class DeleteAccountView(APIView):
    def delete(self, request):
        delete_user(request.user.username)
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
