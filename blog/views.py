from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from .models import Blog, BlogType
from read_count.utils import read_statistics_once_read
from read_count.utils import get_today_hot_data, get_7_days_hot_data
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
import markdown


# 处理博客列表数据
def get_blog_list_common_date(request, blogs_all_list):
    # 使用缓存获取热门博客
    recent_hot_data = cache.get('recent_hot_data')
    if recent_hot_data is None:
        recent_hot_data = get_7_days_hot_data()
        cache.set('recent_hot_data', recent_hot_data, 3600)

    # 获取url的页码参数(GET请求)
    page_num = request.GET.get('page', 1)

    # 每5篇分为一页
    paginator = Paginator(blogs_all_list, 5)

    page_of_blogs = paginator.get_page(page_num)

    # 获取当前页码
    current_page_num = page_of_blogs.number

    # 列表生成式实现页码简短显示(当前页码前后各两页)
    page_range = [x for x in range(current_page_num - 2, current_page_num + 3)
                  if x in paginator.page_range]

    # 加上页面省略页面标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取日期归档下博客数量
    blog_dates = Blog.objects.dates('create_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(create_time__year=blog_date.year,
                                         create_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    content_type = ContentType.objects.get_for_model(Blog)

    context = dict()
    context['today_hot_data'] = get_today_hot_data(content_type)
    context['recent_hot_data'] = recent_hot_data
    context['page_of_blogs'] = page_of_blogs
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['page_range'] = page_range
    context['blog_dates'] = blog_dates_dict
    return context


# 博客列表
def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_date(request, blogs_all_list)
    context['recent_upload_blog'] = Blog.objects \
                                        .values('id', 'title', 'create_time') \
                                        .annotate(read_num_sum=Sum('read_details__read_num')) \
                                        .order_by('-create_time')[:7]
    return render(request, 'blog/blog_list.html', context)


# 博客内容
def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog.objects.select_related().all(), pk=blog_pk)
    blog.content = markdown.markdown(blog.content, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.toc',
    ], safe_mode=True, enable_attributes=False).replace("pre", "pre class='prettyprint linenums'")
    read_cookie_key = read_statistics_once_read(request, blog)

    context = dict()
    context['previous_blog'] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    context['blog'] = blog

    response = render(request, 'blog/blog_detail.html', context)
    if not request.COOKIES.get(read_cookie_key):
        response.set_cookie(read_cookie_key, 'true', max_age=43200)
    return response


# 博客类型
def blog_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_date(request, blogs_all_list)
    context['blog_type'] = blog_type
    return render(request, 'blog/blog_with_type.html', context)


# 博客日期
def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(create_time__year=year, create_time__month=month)
    context = get_blog_list_common_date(request, blogs_all_list)
    context['blogs_with_date'] = '%s年%s月' % (year, month)
    return render(request, 'blog/blog_with_date.html', context)
