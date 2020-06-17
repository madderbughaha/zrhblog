from django.contrib import admin
from .models import LikeRecord

# Register your models here.

@admin.register(LikeRecord)
class LikeRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'liked_time')