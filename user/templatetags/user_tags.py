from django.template import Library
from urllib .parse import urlencode
from zrhblog.settings import base

register = Library()


@register.simple_tag
def get_login_github_url():
    param = {
        'client_id': base.GitHub_APP_ID,
        'redirect_uri': base.GitHub_Redirect,
        'state': base.GitHub_state,
    }

    return 'https://github.com/login/oauth/authorize?' + urlencode(param)
