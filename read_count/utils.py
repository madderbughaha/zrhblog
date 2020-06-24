import datetime
from django.db.models import F, Sum
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


# 获取当天热门博客
def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type, date__lt=today).order_by('-read_num')
    return read_details[:1]


# 获取7天热门博客
def get_7_days_hot_data():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects \
        .filter(read_details__date__lt=today, read_details__date__gte=date) \
        .values('id', 'title', 'create_time') \
        .annotate(read_num_sum=Sum('read_details__read_num')) \
        .order_by('-read_num_sum')
    return blogs[:7]
