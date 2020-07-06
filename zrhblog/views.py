from django.db.models import Count, Sum, Max
from django.http import JsonResponse
from django.shortcuts import render
from read_count.utils import get_seven_days_read_data, get_7_days_hot_data, get_recommend_article, get_hottest_blog
from django.contrib.contenttypes.models import ContentType
from blog.models import Blog, BlogType
from read_count.models import ReadNum
from comment.models import Comment


def home(request):
    context = dict()
    content_type = ContentType.objects.get_for_model(Blog)
    hottest_blog = get_hottest_blog(content_type)[0]
    get_top_five_blog = Blog.objects.order_by('-create_time')[:5]
    get_echarts_item = BlogType.objects.annotate(item_count=Count('blog'))
    total_read_num = ReadNum.objects.aggregate(Sum('read_num'))
    total_blog = Blog.objects.count()
    total_comment = Comment.objects.count()
    recent_comment = Comment.objects.order_by('-comment_time')[:10]

    context['recent_hot_data'] = get_7_days_hot_data()
    context['recent_comment'] = recent_comment
    context['get_top_five_blog'] = get_top_five_blog
    context['get_echarts_item'] = get_echarts_item
    context['total_read_num'] = total_read_num['read_num__sum']
    context['total_blog'] = total_blog
    context['total_comment'] = total_comment
    context['get_recommend_article'] = get_recommend_article()
    context['large_article'] = hottest_blog
    context['recent_upload_blog'] = Blog.objects \
                                        .annotate(read_num_sum=Sum('read_details__read_num')) \
                                        .order_by('-create_time')[:7]
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
