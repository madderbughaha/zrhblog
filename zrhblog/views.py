from django.http import JsonResponse
from django.shortcuts import render
from read_count.utils import get_seven_days_read_data
from django.contrib.contenttypes.models import ContentType
from blog.models import Blog


def home(request):
    context = dict()
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
