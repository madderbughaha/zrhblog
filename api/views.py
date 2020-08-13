from collections import OrderedDict
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.utils import timezone
from read_count.utils import get_seven_days_read_data, get_7_days_hot_data
from rest_framework import viewsets, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from api.serializers import UsersSerializers, LoginSerializer, BlogTypeSerializers, BlogListSerializers
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt import authentication
from blog.models import Blog, BlogType
from comment.models import Comment
from read_count.models import ReadNum, ReadDetail
from .meta import Meta


# 定制分页器
class ResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """分页之后的响应数据格式"""
        pagination = dict()
        pagination['pages'] = self.page.paginator.num_pages
        pagination['page'] = self.page.number
        pagination['total'] = self.page.paginator.count
        return Response(OrderedDict([
            ('pagination', pagination),
            ('results', data)
        ]))


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.validated_data
            return Response(result)
        return Response({'meta': Meta.http_400_bad_request, 'data': 'null'})


class HomeDataView(APIView):
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        data = dict()
        # 文章数量
        blog_count = Blog.objects.count()
        blog_count_rise = '《' + Blog.objects.last().title + '》'

        # 评论数量
        comment_count = Comment.objects.count()
        comment_count_rise = Comment.objects.filter(comment_time=timezone.now()).count()

        # 访问量
        read_num = ReadNum.objects.aggregate(Sum('read_num'))['read_num__sum']
        read_num_rise = ReadDetail.objects.filter(date=timezone.now()).count()

        # 用户人数
        user_count = User.objects.count()
        user_count_rise = User.objects.last().username
        content_type = ContentType.objects.get_for_model(Blog)

        # 7天阅读量
        dates, read_nums = get_seven_days_read_data(content_type)
        data['chart_dates'] = dates
        data['chart_read_nums'] = read_nums

        # 最近热门博客
        data['recent_hot_blog'] = list(get_7_days_hot_data().values('title', 'read_num_sum')[:6])

        # 统计信息
        data['statistics'] = [
            {'icon': 'el-icon-document-add', 'title': '发布的文章', 'count': blog_count, 'rise': blog_count_rise,
             'describe': '最近发表：'},
            {'icon': 'el-icon-chat-round', 'title': '评论数量', 'count': comment_count, 'rise': comment_count_rise,
             'describe': '今日评论数量：'},
            {'icon': 'el-icon-s-data', 'title': '访问量', 'count': read_num, 'rise': read_num_rise,
             'describe': '今日访问量：'},
            {'icon': 'el-icon-s-custom', 'title': '用户人数', 'count': user_count, 'rise': user_count_rise,
             'describe': '最近注册用户：'}]
        result = {'meta': Meta.http_200_ok, 'data': data}
        return Response(result)


class BlogTypeViewSet(viewsets.ModelViewSet):
    queryset = BlogType.objects.all().order_by('id')
    authentication_classes = [authentication.JWTAuthentication]
    serializer_class = BlogTypeSerializers
    permission_classes = [permissions.IsAdminUser]
    pagination_class = ResultsSetPagination

    # 获取博客类型
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = {'meta': Meta.http_200_ok, 'data': serializer.data}
            return self.get_paginated_response(result)

        serializer = self.get_serializer(queryset, many=True)
        result = {'meta': Meta.http_200_ok, 'data': serializer.data}
        return Response(result)

    # 获取单个, /blog_type/x/
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        result = {'meta': Meta.http_200_ok, 'data': serializer.data}
        return Response(result)

    # 新建单个, /blog_type/
    def create(self, request, *args, **kwargs):
        # 如果用户行为是delete,则为批量删除
        if request.data.get('action') == 'delete':
            delete_id = request.data.get('delete_id', None)
            print(delete_id)
            if not delete_id:
                return Response({'meta': Meta.http_404_not_found, 'data': 'null'})
            for i in delete_id.split(','):
                get_object_or_404(BlogType, pk=int(i)).delete()
            return Response({'meta': Meta.http_204_no_content, 'data': 'null'})
        # 新增
        elif request.data.get('action') == 'add':
            serializer = BlogTypeSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'meta': Meta.http_201_created, 'data': serializer.data})
            return Response({'meta': Meta.http_400_bad_request, 'data': serializer.errors})
        # 请求错误
        else:
            return Response({'meta': Meta.http_400_bad_request, 'data': 'null'})

    # 删除单个, /blog_type/x/
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        BlogType.delete(instance)
        return Response({'meta': Meta.http_204_no_content, 'data': 'null'})

    # 更新单个 /blog_type/x/
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = BlogTypeSerializers(instance=instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'meta': Meta.http_205_reset_content, 'data': serializer.data})
        return Response({'meta': Meta.http_404_not_found, 'data': 'null'})


class BlogListViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by('id')
    authentication_classes = [authentication.JWTAuthentication]
    serializer_class = BlogListSerializers
    permission_classes = [permissions.IsAdminUser]
    pagination_class = ResultsSetPagination

    # 获取文章列表
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = {'meta': Meta.http_200_ok, 'data': serializer.data}
            return self.get_paginated_response(result)

        serializer = self.get_serializer(queryset, many=True)
        result = {'meta': Meta.http_200_ok, 'data': serializer.data}
        return Response(result)

    def create(self, request, *args, **kwargs):
        # 如果用户行为是delete,则为批量删除
        if request.data.get('action') == 'delete':
            delete_id = request.data.get('delete_id', None)
            print(delete_id)
            if not delete_id:
                return Response({'meta': Meta.http_404_not_found, 'data': 'null'})
            for i in delete_id.split(','):
                get_object_or_404(Blog, pk=int(i)).delete()
            return Response({'meta': Meta.http_204_no_content, 'data': 'null'})
        # 新增
        elif request.data.get('action') == 'add':
            print(request.data)
            serializer = BlogListSerializers(data=request.data)
            if serializer.is_valid():
                title = serializer.validated_data['title']
                type_name = serializer.validated_data['blog_type']['type_name']
                blog_type = get_object_or_404(BlogType, type_name=type_name)
                author = serializer.validated_data['author']
                content = serializer.validated_data['content']
                pic_800_450 = serializer.validated_data['pic_800_450']
                try:
                    Blog.objects.create(title=title, blog_type=blog_type, author=author, content=content,
                                        pic_800_450=pic_800_450)
                    result = {'meta': Meta.http_200_ok, 'data': 'null'}
                    return Response(result)
                except Exception as e:
                    print(e)
                    result = {'meta': Meta.http_500_internal_server_err, 'data': 'null'}
                    return Response(result)
            else:
                print(serializer.errors)
                result = {'meta': Meta.http_400_bad_request, 'data': serializer.errors}
                return Response(result)
        # 请求错误
        else:
            print(request.data)
            return Response({'meta': Meta.http_400_bad_request, 'data': '请检查是否填写操作行为:‘action’'})

    # 删除单个, /blog/x/
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        Blog.delete(instance)
        return Response({'meta': Meta.http_204_no_content, 'data': 'null'})


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializers
    permission_classes = [permissions.IsAuthenticated]
