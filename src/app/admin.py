from django.contrib import admin

from .models import Invitation, RSVP
# Register your models here.


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("couple_name", "wedding_date", "location", "created_at", "publish")
    date_hierarchy = "created_at"
    list_per_page = 10
    list_editable = ["publish"]
    

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ("full_name", "token", "guests_count", "is_present", "created_at", "publish")
    date_hierarchy = "created_at"
    list_per_page = 10
    list_editable = ["publish"]