from django.utils.html import strip_tags
from notifications.signals import notify
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LikeRecord


@receiver(post_save, sender=LikeRecord)
def send_notification(sender, instance, **kwargs):
    # 发送站内消息
    if instance.content_type.model == 'blog':
        blog = instance.content_object
        verb = '赞了我的文章'.format(instance.user.get_nickname_or_username())
        description = '{0}'.format(blog.content)
    elif instance.content_type.model == 'comment':
        comment = instance.content_object
        verb = '赞了我的评论'.format(instance.user.get_nickname_or_username())
        description = '{0}'.format(strip_tags(comment.text))
    recipient = instance.content_object.get_user()
    url = instance.content_object.get_url()
    if not instance.user == recipient:
        notify.send(instance.user, recipient=recipient, verb=verb, action_object=instance, description=description,
                    url=url)
