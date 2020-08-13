from blog.models import Blog, BlogType
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.response import Response


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        meta = dict()
        data = dict()
        try:
            data = super().validate(attrs)
            if not self.user.is_superuser:
                data['data'] = 'null'
                meta['status'] = status.HTTP_403_FORBIDDEN
                meta['message'] = '无权登录，您不是管理员'
                data.pop('access')
                data.pop('refresh')
            else:
                data['token'] = data.pop('access')
                data['nickname'] = self.user.get_nickname_or_username()
                meta['status'] = status.HTTP_200_OK
                meta['message'] = '登录成功'
        except AuthenticationFailed:
            meta['status'] = status.HTTP_401_UNAUTHORIZED
            meta['message'] = '登录失败，用户名或密码错误'
            data['data'] = 'null'
        result = {'meta': meta, 'data': data}
        return result


class BlogTypeSerializers(serializers.ModelSerializer):
    class Meta:
        model = BlogType
        fields = ['id', 'type_name']


class BlogListSerializers(serializers.ModelSerializer):
    # 外键关联
    blog_type = serializers.CharField(source='blog_type.type_name')
    author_info = serializers.SerializerMethodField()
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False, read_only=True)
    last_update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False, read_only=True)

    def get_author_info(self, obj):
        return obj.author.get_nickname_or_username()

    class Meta:
        model = Blog
        fields = ['id', 'title', 'blog_type', 'author_info', 'author', 'content', 'get_read_num', 'create_time',
                  'last_update_time',
                  'pic_800_450']
        extra_kwargs = {'author': {"write_only": True}, 'content': {'write_only': True}}


class UsersSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
