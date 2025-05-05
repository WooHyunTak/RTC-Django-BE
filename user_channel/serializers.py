from rest_framework import serializers
from user.serializers import UserMainSerializer
from .models import UserChannel

class UserChannelCreateSerializer(serializers.ModelSerializer):
    created_by = UserMainSerializer(read_only=True)
    def create(self, validated_data):
        created_by_id = self.context.get("created_by")
        return UserChannel.objects.create(created_by_id=created_by_id, **validated_data)

    class Meta:
        model = UserChannel
        fields = ("name", "description", "created_by")

class UserChannelSerializer(serializers.ModelSerializer):
    created_by = UserMainSerializer(read_only=True)

    class Meta:
        model = UserChannel
        fields = ("id", "name", "description", "created_by")
