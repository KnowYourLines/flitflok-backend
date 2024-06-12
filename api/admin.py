import os

import mux_python
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from firebase_admin.auth import delete_user, delete_users

from api.models import Video, User

configuration = mux_python.Configuration()
configuration.username = os.environ["MUX_TOKEN_ID"]
configuration.password = os.environ["MUX_TOKEN_SECRET"]
assets_api = mux_python.AssetsApi(mux_python.ApiClient(configuration))


class ReportedVideoListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Reported Videos")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "reported"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [
            (True, _("Reported")),
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(reported_by__isnull=False)


class VideoModelAdmin(admin.ModelAdmin):
    readonly_fields = ["creator", "display_video"]
    fields = ["creator", "display_video"]
    search_fields = ["id"]
    list_filter = [ReportedVideoListFilter]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def display_video(self, obj):
        url = f"https://stream.new/v/{obj.playback_id}"
        return mark_safe("<a href='%s' target='_blank' >View</a>" % url)

    def delete_model(self, request, obj):
        assets_api.delete_asset(obj.asset_id)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for video in queryset.all():
            assets_api.delete_asset(video.asset_id)
        super().delete_queryset(request, queryset)

    display_video.short_description = "Video"


class UserModelAdmin(admin.ModelAdmin):
    search_fields = ["username"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def delete_model(self, request, obj):
        delete_user(obj.username)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        users = [user.username for user in queryset.all()]
        delete_users(users)
        super().delete_queryset(request, queryset)


admin.site.register(Video, VideoModelAdmin)
admin.site.register(User, UserModelAdmin)
