from django.utils.html import strip_tags
from notifications.signals import notify
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment


@receiver(post_save, sender=Comment)
def send_notification(sender, instance, **kwargs):
    # 发送站内消息
    if instance.reply_to is None:
        # 评论
        recipient = instance.content_object.get_user()
        if instance.content_type.model == 'blog':
            blog = instance.content_object
            verb = '在文章《{0}》中发表评论:'.format(blog.title)
            description = '{0}'.format(strip_tags(instance.text))
        else:
            raise Exception('unknown comment object type')
    else:
        # 回复
        recipient = instance.reply_to
        if len(instance.parent.text) > 20:
            instance.parent.text = instance.parent.text[:10] + '...'
        verb = '在评论"{0}"中回复了我:'.format(strip_tags(instance.parent.text))
        description = '@{0}：{1}'.format(instance.reply_to.get_nickname_or_username(), strip_tags(instance.text))
    url = instance.content_object.get_url() + "#root_" + str(instance.pk)
    if not instance.user == recipient:
        notify.send(instance.user, recipient=recipient, verb=verb, action_object=instance, description=description,
                    url=url)
