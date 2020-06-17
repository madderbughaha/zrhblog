from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from notifications.models import Notification
from likes.models import LikeRecord
from comment.models import Comment


# 我的通知
def my_notifications(request):
    context = dict()
    like_content_type = ContentType.objects.get_for_model(LikeRecord)
    comment_content_type = ContentType.objects.get_for_model(Comment)
    system_content_type = ContentType.objects.get_for_model(User)
    notify_for_like = request.user.notifications.all().filter(action_object_content_type=like_content_type)
    notify_for_comment = request.user.notifications.all().filter(action_object_content_type=comment_content_type)
    notify_for_system = request.user.notifications.all().filter(action_object_content_type=system_content_type)
    context['notify_for_like'] = notify_for_like
    context['notify_for_comment'] = notify_for_comment
    context['notify_for_system'] = notify_for_system
    return render(request, 'notify/my_notifications.html', context)


# 处理通知状态
def resolve_notify(request):
    my_notification_pk = request.GET.get('my_notification_pk', '')
    data = dict()
    if my_notification_pk != '':
        try:
            my_notification = get_object_or_404(Notification, pk=my_notification_pk)
            my_notification.unread = False
            my_notification.save()
            data['status'] = 'SUCCESS'
            data['url'] = my_notification.data['url']
        except ObjectDoesNotExist:
            data['status'] = '该通知不存在！'
    else:
        data['status'] = '请求异常！'
    return JsonResponse(data)


# 全部标记为已读
def mark_all_as_read(request):
    data = dict()
    notification_id = request.GET.get('action_type_id', '')
    if notification_id != '':
        try:
            notifications = Notification.objects.filter(recipient=request.user,
                                                        action_object_content_type_id=notification_id)
            notifications.mark_all_as_read()
            data['status'] = '200'
        except ObjectDoesNotExist:
            data['status'] = '通知对象不存在！'
    else:
        data['status'] = '请求异常！'
    return JsonResponse(data)


# 删除通知
def delete_notify(request):
    notification_id = request.GET.get('notification_id', '')
    data = dict()
    if notification_id != '':
        # 执行删除
        try:
            notification = get_object_or_404(Notification, pk=notification_id)
            notification.delete()
            data['status'] = '200'
        except ObjectDoesNotExist:
            data['status'] = '通知对象不存在！'

    else:
        # 返回错误
        data['status'] = '请求异常！'
    return JsonResponse(data)
