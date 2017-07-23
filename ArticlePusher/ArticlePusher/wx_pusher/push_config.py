# coding: utf-8
# 自定义功能分组和推送对象
# 推送对象：个人和群聊
# 格式：
# {
#   功能名：{
#       分类名：(单人对象组名，群聊对象组名)
#       }
# }
# 单人对象或群聊对象加入对应组名的推送组里
PUSH_CONFIG = {
    'tech': {
        'article': ('tech_article_single', 'tech_article_groups')
    },
    'opera': {
        'british': ('opera_british_single', 'opera_british_groups'),
        'america': ('opera_america_single', 'opera_america_groups')
    }
}
