from rest_framework import serializers

from message.models import Message
from user.serializers import UserMainSerializer

from .models import UserChannel


class UserChannelCreateSerializer(serializers.ModelSerializer):
    created_by = UserMainSerializer(read_only=True)
    members = UserMainSerializer(read_only=True, many=True)

    def create(self, validated_data):
        created_by_id = self.context.get("created_by")
        return UserChannel.objects.create(created_by_id=created_by_id, **validated_data)

    class Meta:
        model = UserChannel
        fields = ("name", "description", "created_by", "is_private", "type", "members")


class UserChannelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChannel
        fields = ("id", "name", "is_private", "type")


class UserChannelSerializer(serializers.ModelSerializer):
    created_by = UserMainSerializer(read_only=True)
    members = UserMainSerializer(read_only=True, many=True)

    class Meta:
        model = UserChannel
        fields = (
            "id",
            "name",
            "description",
            "created_by",
            "is_private",
            "type",
            "members",
        )


class UserChannelMessageSerializer(serializers.ModelSerializer):
    from_user = UserMainSerializer(read_only=True)

    class Meta:
        model = Message
        fields = (
            "id",
            "from_user",
            "content",
            "root_message",
            "created_at",
        )


class UserDMChannelListSerializer(serializers.ModelSerializer):
    to_user = serializers.SerializerMethodField()

    class Meta:
        model = UserChannel
        fields = (
            "id",
            "to_user",
        )

    def get_to_user(self, obj):
        try:
            from_user_id = self.context.get("from_user_id")
            to_user = obj.members.exclude(id=from_user_id).get()
            return UserMainSerializer(to_user).data if to_user else None
        except Exception:
            return None
