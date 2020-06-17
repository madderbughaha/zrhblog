from django.template import Library

register = Library()

# 估计阅读时长
@register.filter
def ReadTime(striptags):
    count = striptags.replace(" ", "")
    if len(count) < 500:
        return 1
    else:
        return len(count) // 500

# 统计文章字数
@register.filter(name='TextCount')
def TextCount(striptags):
    text = striptags.replace(" ", "")
    nums = len(text)
    if nums > 1000:
        nums = nums / 1000
        return str(round(nums, 2)) + 'k'
    return nums

