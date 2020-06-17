from .forms import CommentForm
from .models import Comment
from django.http import JsonResponse
from django.contrib.contenttypes.fields import ContentType


# 提交评论
def submit_comment(request):
    comment_form = CommentForm(request.POST, user=request.user)

    data = dict()
    if comment_form.is_valid():
        # 检查通过,保存数据
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_obj']
        parent = comment_form.cleaned_data['parent']
        if parent:
            comment.root = parent.root if parent.root else parent
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()

        data['status'] = 'SUCCESS'
        data['username'] = comment.user.get_nickname_or_username()
        data['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M')
        data['text'] = comment.text
        data['content_type'] = ContentType.objects.get_for_model(comment).model
        if parent:
            data['reply_to'] = comment.reply_to.get_nickname_or_username()
        else:
            data['reply_to'] = ''
        if data['username'] == request.user.get_nickname_or_username():
            data['is_myself'] = 'true'
        else:
            data['is_myself'] = 'false'
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if comment.root else ''
    else:
        # return render(request, 'error.html', {'message': comment_form.errors, 'referer_to': referer})
        data['error'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]
    # 返回数据
    return JsonResponse(data)
