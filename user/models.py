from django.db import models
from django.contrib.auth.models import User


class OAuthRelationShip(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    open_id = models.CharField(max_length=128)
    OAUTH_TYPE_CHOICE = (
        (0, 'QQ'),
        (1, 'GitHub'),
        (2, 'WeChat'),
        (3, 'Sina'),
    )
    oauth_type = models.IntegerField(default=0, choices=OAUTH_TYPE_CHOICE)

    def __str__(self):
        return "<OAuthRelationShip: %s>" % self.user.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20, verbose_name='昵称')

    def __str__(self):
        return '<Profile: %s for %s>' % (self.nickname, self.user.username)


# 动态绑定昵称
def get_nickname_or_username(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return self.username


User.get_nickname_or_username = get_nickname_or_username
