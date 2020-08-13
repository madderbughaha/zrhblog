from rest_framework import status


class Meta:
    http_200_ok = {'status': status.HTTP_200_OK, 'message': '请求成功'}
    http_400_bad_request = {'status': status.HTTP_400_BAD_REQUEST, 'message': '请求失败,请检查输入数据'}
    http_404_not_found = {'status': status.HTTP_404_NOT_FOUND, 'message': '删除失败,要删除的对象不存在'}
    http_204_no_content = {'status': status.HTTP_204_NO_CONTENT, 'message': '删除成功'}
    http_201_created = {'status': status.HTTP_201_CREATED, 'message': '新增成功'}
    http_500_internal_server_err = {'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': '未知错误，请联系管理员'}
    http_205_reset_content = {'status': status.HTTP_205_RESET_CONTENT, 'message': '修改成功'}