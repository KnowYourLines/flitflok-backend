import datetime

from django.contrib import admin
from django.utils.safestring import mark_safe
from firebase_admin import storage
from firebase_admin.auth import delete_user

from api.models import Video, User


class VideoModelAdmin(admin.ModelAdmin):
    readonly_fields = ["creator", "display_video"]
    fields = ["creator", "display_video"]
    search_fields = ["id"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def display_video(self, obj):
        bucket = storage.bucket()
        blob = bucket.blob(str(obj.file_id))
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(days=7),
            method="GET",
        )
        return mark_safe("<a href='%s' target='_blank' >View</a>" % url)

    def delete_model(self, request, obj):
        bucket = storage.bucket()
        blob = bucket.blob(str(obj.file_id))
        blob.delete()
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        bucket = storage.bucket()
        for video in queryset.all():
            blob = bucket.blob(str(video.file_id))
            blob.delete()
        super().delete_queryset(request, queryset)

    display_video.short_description = "Video"


class UserModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def delete_model(self, request, obj):
        delete_user(obj.username)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for user in queryset.all():
            delete_user(user.username)
        super().delete_queryset(request, queryset)


admin.site.register(Video, VideoModelAdmin)
admin.site.register(User, UserModelAdmin)
