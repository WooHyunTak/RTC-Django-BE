from rest_framework import serializers
from .models import UserMain, UserProfile


class UserMainSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = UserMain
        fields = (
            "id",
            "name",
            "email",
            "profile",
        )

    def get_profile(self, obj):
        try:
            profile = UserProfile.objects.get(user=obj)
            return UserProfileSerializer(profile).data
        except Exception:
            return None


class UserMainListSerializer(serializers.ModelSerializer):
    # include nested UserProfile data
    profile = serializers.SerializerMethodField()

    class Meta:
        model = UserMain
        fields = (
            "id",
            "name",
            "email",
            "profile",
        )

    def get_profile(self, obj):
        try:
            # default related name for OneToOneField is 'userprofile'
            profile = obj.userprofile
        except Exception:
            return None
        # import here to avoid circular reference at class creation
        from .serializers import UserProfileListSerializer

        return UserProfileListSerializer(profile).data


class UserMainCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMain
        fields = (
            "id",
            "name",
            "email",
            "password",
        )
        read_only_fields = ("id",)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user",
            "image_url",
        )


class UserProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user",
            "image_url",
        )
