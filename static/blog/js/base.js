/* 首页 */

//动态定义粒子特效
let script = $("<script id='c_n_script' src='/static/blog/js/lizi.js' color='0,0,0'pacity='0.7' count='100' zindex='-2'>")
$('body').append(script);

//窗体改变大小事件
$(window).resize(function () {
    let body_height = $('.container').outerHeight(true); //正文高度
    let bottom_height = $('.panel-footer').outerHeight(true); //底部元素高度
    let window_height = $(window).height(); //浏览器页面高度

    //判断并调整底部元素的样式
    if ($(".panel-footer").hasClass('page-bottom')) {
        //若包含有page-bottom类，就应用了position设置
        //当position为absolute时，body高度不包含这个元素
        //所以页面高度需要判断body和footer之和若小于浏览器窗口
        //则移除样式，让footer自然跟随在正文后面
        if (body_height + bottom_height + 70 >= window_height) {
            $(".panel-footer").removeClass('page-bottom');
        }
    } else {
        //若没有page-bottom类，body高度包含footer
        //判断body高度小于浏览器时，则悬浮于底部
        if (body_height < window_height) {
            $(".panel-footer").addClass('page-bottom');
        }
    }
});
$(window).trigger('resize')

//显示最近阅读量图表
$('.show-read-num').click(function () {
    let show_read_num = $('.show-read-num').text().trim()
    if (show_read_num == '最近阅读量') {
        $.ajax({
            url: "/base/",
            dataType: "json",
            success: function (data) {
                dates = data.dates;
                nums = data.nums;
                // 图表配置
                options = {
                    chart: {
                        type: 'line'                          //指定图表的类型，默认是折线图（line）
                    },
                    title: {
                        text: '近7天阅读量'                 // 标题
                    },
                    xAxis: {
                        title: {text: '7日阅读量'},
                        categories: dates,        // x 轴分类
                        tickmarkPlacement: 'on',
                    },
                    yAxis: {
                        title: null,             // y 轴标题},
                        labels: {enabled: false},
                        gridLineDashStyle: 'Dash',
                    },
                    series: [{                              // 数据列
                        name: '阅读量',                        // 数据列名
                        data: nums,                     // 数据
                    }],
                    plotOptions: {
                        line: {
                            dataLabels: {
                                enabled: true
                            }
                        }
                    },
                    legend: {enabled: false},
                    credits: {enabled: false},
                };
                // 图表初始化函数
                let chart = Highcharts.chart('read-num-container', options);
            }
        })
        $('#read-num-container').removeClass('container-hidden')
        $('.show-read-num').text('关闭图表')
    }
    if (show_read_num == '关闭图表') {
        $('#read-num-container').addClass('container-hidden')
        $('.show-read-num').text('最近阅读量')
    }
})


/* 博客列表页 */

//tab hover事件
$('.tab-head a').hover(function () {
    if (!$(this).find('a').hasClass('tab-active')) {
        $(this).addClass('tab-a-black')
    }
}, function () {
    if (!$(this).find('a').hasClass('tab-active')) {
        $(this).removeClass('tab-a-black')
    }
});

//tab 点击事件
$(".tab-head li").click(function () {
    let index = $(this).index();
    let a = $(this).find('a');

    if (!a.hasClass('tab-active')) {
        a.addClass('tab-active')
        $(this).siblings().find('a').removeClass('tab-active')
    }
    $('.tab-content .tab-item').eq(index).show().siblings().hide()
});


/* 登录页 */

//input聚焦,错误信息消失
$('.loginBox input').focus(function () {
    if ($('.auth-faild').text() != null) {
        $('.auth-faild').text('')
    }
});
$('.registerBox input').focus(function () {
    if ($('.auth-faild').text() != null) {
        $('.auth-faild').text('')
    }
});

//显示密码
$('.pwdshow').click(function () {
    if ($(this).find('span').hasClass('glyphicon-eye-close')) {
        $(this).find('span').removeClass('glyphicon-eye-close')
        $(this).find('span').addClass('glyphicon-eye-open')
        $('input[name=password]').attr("type", "text");
        $('input[name=pwd_again]').attr("type", "text");
    } else {
        $(this).find('span').removeClass('glyphicon-eye-open')
        $(this).find('span').addClass('glyphicon-eye-close')
        $('input[name=password]').attr("type", "password");
        $('input[name=pwd_again]').attr("type", "password");
    }

});


/* 博客详情页 */

//自定义format方法
String.prototype.format = function () {
    let str = this;
    for (let i = 0; i < arguments.length; i++) {
        str = str.replace(new RegExp('\\{' + i + '\\}', 'g'), arguments[i])
    }
    return str;
}

//提交评论(ajax更新数据)
$('#comment-form').submit(function () {
    //清楚错误信息
    let comment_error = $('#comment-error');
    let reply_comment_id = $('#reply_comment_id');
    let comment_count = $('#comment_count');
    comment_error.text('');
    //判断评论内容是否为空
    if (CKEDITOR.instances['id_text'].document.getBody().getText().trim() === "") {
        comment_error.text('评论内容不能为空！');
        return false;
    }

    // 更新数据到textarea
    CKEDITOR.instances['id_text'].updateElement();

    //异步提交
    $.ajax({
        url: "/comment/submit_comment/",
        type: "POST",
        data: $(this).serialize(),
        cache: false,
        success: function (data) {
            if (data['status'] === 'SUCCESS') {
                if (reply_comment_id.val() === '0') {
                    //插入评论
                    let comment_html = '';
                    console.log(data['is_myself'])
                    if (data['is_myself'] === 'false') {
                        comment_html = '<div class="media comment-list-detail"> <div class="media-left media-middle comment-list-detail-img"> <img class="media-object img-circle" src="/static/blog/img/comment-list-img.jpg"alt="..."> </div> <div  id="root_{0}" class="media-body comment-list-detail-body"> <h5 class="media-heading comment-list-detail-body-user">{1}</h5> <p id="comment-{0}" class="comment-list-detail-body-content">{2}</p> <div class="comment-list-detail-body-info"><span class="comment-list-detail-body-info-time">{3}</span> <span class="comment-like" onclick="likeChanged(this,\'{4}\',{0})"> <span class="like-icon iconfont icon-praise_icon"></span> <span class="like-num">0</span> </span> <a href="javascript:reply({0});">回复</a> </div></div></div>';
                    } else {
                        comment_html = '<div class="media comment-list-detail"> <div class="media-left media-middle comment-list-detail-img"> <img class="media-object img-circle" src="/static/blog/img/comment-list-img.jpg"alt="..."> </div> <div  id="root_{0}" class="media-body comment-list-detail-body"> <h5 class="media-heading comment-list-detail-body-user">{1}</h5> <p id="comment-{0}" class="comment-list-detail-body-content">{2}</p> <div class="comment-list-detail-body-info"><span class="comment-list-detail-body-info-time">{3}</span> <span class="comment-like" onclick="likeChanged(this,\'{4}\',{0})"> <span class="like-icon iconfont icon-praise_icon"></span> <span class="like-num">0</span> </span></div></div></div>';
                    }
                    comment_html = comment_html.format(data['pk'], data['username'], data['text'], data['comment_time'], data['content_type'],)
                    $('#comment-list').append(comment_html);
                    let comment_count = parseInt(comment_count.text()) + 1;
                    comment_count.text(comment_count)
                } else {
                    //回复评论
                    let reply_html = '<div class="media comment-list-detail"><div class="media-left media-middle comment-list-detail-reply-img"><img class="media-object img-circle"src="/static/blog/img/comment-list-img.jpg"alt="..."></div><div class="media-body reply-list-detail-body comment-list-detail-body"><h5 class="media-heading comment-list-detail-body-user">{0}</h5><p id="comment-{1}"class="comment-list-detail-body-content">{2}</p><div class="comment-list-detail-body-info"><span class="comment-list-detail-body-info-time">{3}</span> <span class="comment-like" onclick="likeChanged(this,\'{4}\',{1})"> <span class="like-icon iconfont icon-praise_icon"></span> <span class="like-num">0</span> </span> <a href="javascript:reply({1});">回复</a></div></div></div>';
                    reply_html = reply_html.format(data['username'], data['pk'], data['text'], data['comment_time'], data['content_type'])
                    $("#root_" + data['root_pk']).append(reply_html);
                }
                //清空编辑框内容
                CKEDITOR.instances['id_text'].setData('');
                $('#reply-content-container').hide();
                reply_comment_id.val('0');
                $('.none-comment').remove();
                comment_error.text('评论成功~')
            } else {
                //显示错误信息
                comment_error.text(data['message'])
            }
        },
        error: function (xhr) {
            console.log(xhr);
        }
    });
    return false;
});

//回复评论
function reply(reply_comment_id) {
    $('#reply_comment_id').val(reply_comment_id);
    let html = $("#comment-" + reply_comment_id).next().html();
    $('#reply-content').html(html);
    $('#reply-content-container').show();
    $('html,body').animate({scrollTop: $('#comment-form').offset().top - 60}, 300, function () {
        CKEDITOR.instances['id_text'].focus()
    });
}

//点赞功能
function likeChanged(obj, conntent_type, object_id) {
    let is_like = obj.getElementsByClassName('active').length === 0;
    $.ajax({
        url: "/like/like_change",
        type: 'GET',
        data: {
            content_type: conntent_type,
            object_id: object_id,
            is_like: is_like,
        },
        cache: false,
        success: function (data) {
            console.log(data);
            if (data['status'] === 'SUCCESS') {
                let element = $(obj.getElementsByClassName('like-icon'));
                console.log(element, is_like);
                // 更新点赞状态
                if (is_like) {
                    element.addClass('active')
                } else {
                    element.removeClass('active')
                }
                let like_num = $(obj.getElementsByClassName('like-num'));
                // 更新点赞数量
                like_num.text(data['like_num'])
            } else {
                if (data['code'] === 400) {
                    $('#loginModal').modal('show');
                } else {
                    alert(data['message'])
                }
            }
        },
        error: function (xhr) {
            console.log(xhr)
        }
    });
}

//模态框登录
$('#login-modal-form').submit(function (event) {
    event.preventDefault();
    $.ajax({
        url: '/user/login_for_modal/',
        type: 'POST',
        data: $(this).serialize(),
        cache: false,
        success: function (data) {
            if (data['status'] === 'SUCCESS') {
                console.log(data['status']);
                window.location.reload();
            } else {
                $('#login-modal-tip').text('用户名或密码不正确');
            }
        }
    });
})

//评论跳转
$(function () {
    if (window.location.hash) {
        $("html,body").stop(true);
        $('html,body').animate({scrollTop: $(window.location.hash).offset().top - 70}, 500);
    }
});

//取消回复
$('.cancle-reply').click(function () {
    let reply_comment_id = $('#reply_comment_id');
    $('#reply-content-container').hide();
    $('html,body').animate({scrollTop: $('#comment-'+reply_comment_id.val()).offset().top - 140}, 300);
    reply_comment_id.val('0');
});

