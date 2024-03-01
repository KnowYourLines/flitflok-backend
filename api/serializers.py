from rest_framework import serializers

from api.models import User


class EulaAgreedSerializer(serializers.Serializer):
    agree = serializers.BooleanField(required=True)

    def update(self, user, validated_data):
        user.agreed_to_eula = validated_data.get("agree", user.agreed_to_eula)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["agreed_to_eula"]
