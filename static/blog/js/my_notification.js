//侧边栏点击事件
$(".message-space-left-list li").click(function () {
    let index = $(this).index();
    let a = $(this).find('a');

    if (!a.hasClass('active')) {
        a.addClass('active');
        $(this).siblings().find('a').removeClass('active');
        $(this).siblings().find('a').css('color', '#6b757b')
    }
    $('.message-title').eq(index).show().siblings('.message-title').hide();
    $('.message-space-right .messsage-content').eq(index).show().siblings('.messsage-content').hide()
});

//弹出删除模态框
$('.delete-notify').on('click', function (e) {
    let delete_data_id = $(this).attr('id').split('-')[2];
    let modal_dialog = $('#deleteModal');
    modal_dialog.on('show.bs.modal', function () {
        //传入delete_data_id,提交删除
        $('#object_id').val(delete_data_id);
    });
    modal_dialog.modal('show');
    e.stopPropagation()
});

//删除通知
$('.modal-delete-submit').click(function () {
    let notification_id = $('#object_id').val();
    $.ajax({
        url: '/notify/delete_notify/',
        type: 'GET',
        cache: false,
        data: {
            'notification_id': notification_id
        },
        success: function (data) {
            if (data['status'] === '200') {
                $('#deleteModal').modal('hide');
                $('#media-data-' + notification_id).fadeOut();
            }
            else{
                console.log(data['status'])
            }
        },
        error: function (xhr) {
            console.log(xhr)
        }
    })
});

//全部标记为已读
$('.mark-all').on('click', function () {
    let action_type_id = $(this).attr('id');
    if (action_type_id !== '') {
        $.ajax({
            url: '/notify/mark_all_as_read/',
            type: 'GET',
            data: {
                action_type_id: action_type_id
            },
            cache: false,
            success: function (data) {
                if (data['status'] === '200') {
                    let message_card = "#message-card-" + action_type_id;
                    let item = '#item-' + action_type_id;
                    console.log($(message_card));
                    $(message_card).find('.new-notify').fadeOut();
                    $(item).find('.unread').fadeOut();
                } else {
                    console.log(data['status'])
                }
            },
            error: function (xhr) {
                console.log(xhr)
            }
        })
    }
});

//跳转至详情
$('.media').on('click', function () {
    let media_data_id = $(this).attr('id').split('-')[2];
    console.log(media_data_id);
    if ($(this).parents('#message-card-12').length === 1) {
        console.log('this is like');
        return false
    } else {
        $.ajax({
            url: '/notify/resolve_notify/',
            type: 'GET',
            cache: false,
            data: {
                'my_notification_pk': media_data_id
            },
            success: function (data) {
                console.log(data);
                let target_url = data['url'];
                window.open(target_url, '_self')
            },
            error: function (xhr) {
                console.log(xhr)
            }
        })
    }
});