import datetime

from django.core.cache import cache
from django.db.models import F, Sum, Max
from django.contrib.contenttypes.models import ContentType
from .models import ReadDetail, ReadNum
from django.utils import timezone
from blog.models import Blog


# 获取文章阅读量
def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)

    if not request.COOKIES.get(key):
        # 当前阅读量+1
        read_obj = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)[0]
        read_obj.read_num = F('read_num') + 1
        read_obj.save()
        read_obj.refresh_from_db()

        # 当天阅读量+1
        date = timezone.now()
        date_read_obj = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)[0]
        date_read_obj.read_num = F('read_num') + 1
        date_read_obj.save()
        read_obj.refresh_from_db()
    return key


# 获取7天阅读数据
def get_seven_days_read_data(content_type):
    today = timezone.now()
    read_nums = []
    dates = []
    for i in range(7, 0, -1):
        # 计算日期差量
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        read_detail = ReadDetail.objects.filter(content_type=content_type, date=date)
        # 求当天阅读量之和
        result = read_detail.aggregate(read_num_sum=Sum('read_num'))
        read_nums.append(result['read_num_sum'] or 0)
    return dates, read_nums


# 获取最热博客
def get_hottest_blog(content_type):
    object_id = ReadDetail.objects.filter(content_type=content_type).values('object_id').order_by('-read_num').first()
    content_object = content_type.model_class().objects.all().filter(id=object_id['object_id'])
    return content_object


# 获取7天热门博客
def get_7_days_hot_data():
    # 使用缓存获取热门博客
    recent_hot_data = cache.get('recent_hot_data')

    if recent_hot_data is None:
        today = timezone.now().date()
        date = today - datetime.timedelta(days=7)
        blogs = Blog.objects \
            .filter(read_details__date__lt=today, read_details__date__gte=date) \
            .annotate(read_num_sum=Sum('read_details__read_num')) \
            .order_by('-read_num_sum')
        recent_hot_data = blogs[:7]
        cache.set('recent_hot_data', recent_hot_data, 3600)
    return recent_hot_data


# 获取随机文章

def get_recommend_article():
    # 使用缓存获取推荐博客
    recommend_article = cache.get('recommend_article')
    if recommend_article is None:
        recommend_article = Blog.objects.order_by('?')[:4]
        cache.set('recommend_article', recommend_article, 86400)
    return recommend_article
