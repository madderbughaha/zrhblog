from django.core.cache import cache
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import render
from read_count.utils import get_seven_days_read_data,get_today_hot_data
from django.contrib.contenttypes.models import ContentType
from blog.models import Blog, BlogType
from read_count.models import ReadNum
from comment.models import Comment


def get_recommend_article():
    # 使用缓存获取热门博客
    recommend_article = cache.get('recommend_article')
    if recommend_article is None:
        recommend_article = Blog.objects.order_by('?')[:4]
        cache.set('recommend_article', recommend_article, 86400)
    return recommend_article


def home(request):
    context = dict()
    content_type = ContentType.objects.get_for_model(Blog)
    get_top_five_blog = Blog.objects.order_by('-create_time')[:5]
    get_echarts_item = BlogType.objects.annotate(item_count=Count('blog'))
    get_large_article = get_today_hot_data(content_type)
    total_read_num = ReadNum.objects.aggregate(Sum('read_num'))
    total_blog = Blog.objects.count()
    total_comment = Comment.objects.count()

    context['get_top_five_blog'] = get_top_five_blog
    context['get_echarts_item'] = get_echarts_item
    context['total_read_num'] = total_read_num['read_num__sum']
    context['total_blog'] = total_blog
    context['total_comment'] = total_comment
    context['get_recommend_article'] = get_recommend_article()
    context['get_large_article'] = get_large_article
    return render(request, 'home.html', context)


def base(request):
    if request.is_ajax():
        content_type = ContentType.objects.get_for_model(Blog)
        dates, read_nums = get_seven_days_read_data(content_type)

        context = dict()
        context['dates'] = dates
        context['nums'] = read_nums
        response = JsonResponse(context)
        return response
