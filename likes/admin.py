from django.contrib import admin
from .models import LikeRecord, LikeCount


# Register your models here.

@admin.register(LikeRecord)
class LikeRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'liked_time')


@admin.register(LikeCount)
class LikeCount(admin.ModelAdmin):
    list_display = ('object_id', 'liked_num')
