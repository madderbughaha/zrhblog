from django.contrib import admin
from .models import BlogType, Blog


@admin.register(BlogType)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name')


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    # 要显示的字段
    fieldsets = (
        ('base_info', {'fields': ['title', 'blog_type']}),
        ('content', {'fields': ['pic_800_450', 'content']})
    )

    list_display = (
        'id', 'title', 'blog_type', 'author', "get_read_num", 'create_time', 'last_update_time', 'pic_800_450')

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()

    def get_form(self, request, obj=None, change=False, **kwargs):
        self.exclude = ('author', '')
        form = super(BlogAdmin, self).get_form(request, obj, **kwargs)
        return form


admin.site.site_header = '博客后台管理'
admin.site.site_title = 'ZrhBLOG后台管理'
