from django.contrib import admin
from .models import BlogType, Blog


@admin.register(BlogType)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name')


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    # 要显示的字段
    list_display = ('id', 'title', 'blog_type', 'author', "get_read_num", 'create_time', 'last_update_time')