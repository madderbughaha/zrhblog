from django.template import Library
from ..models import Comment
from ..forms import CommentForm
from django.contrib.contenttypes.models import ContentType

register = Library()


@register.simple_tag
def get_comment_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type=content_type, object_id=obj.pk).count()
    if comments:
        return comments
    return 0


@register.simple_tag
def get_comment_form(obj):
    content_type = ContentType.objects.get_for_model(obj)
    form = CommentForm(initial={'content_type': content_type.model,
                                'object_id': obj.pk, 'reply_comment_id': 0})
    return form


@register.simple_tag
def get_comment_list(obj):
    content_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type=content_type, object_id=obj.pk, parent=None)
    return comments.order_by('comment_time')