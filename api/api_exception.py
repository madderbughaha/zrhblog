from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data.clear()
        response.data['status'] = response.status_code
        response.data['data'] = 'null'

        if response.status_code == 404:
            try:
                response.data['message'] = response.data.pop('detail')
                response.data['message'] = "请求不存在，请检查后再试"
            except KeyError:
                response.data['message'] = "请求不存在，请检查后再试"

        if response.status_code == 400:
            response.data['message'] = "请求异常，请稍后再试"

        elif response.status_code == 401:
            response.data['message'] = "认证失败，请重新尝试"

        elif response.status_code >= 500:
            response.data['message'] = "服务器错误，请联系管理员"

        elif response.status_code == 403:
            response.data['message'] = "权限不允许, 请联系管理员"

        elif response.status_code == 405:
            response.data['message'] = '请求不允许， 请联系管理员'
    else:
        response.data['message'] = "未知错误, 请联系管理员"
    return response
