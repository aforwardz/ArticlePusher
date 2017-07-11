# coding: utf-8
import redis
import wxpy
from datetime import date
from ArticlePusher import settings
import logging

push_logger = logging.getLogger('push_logger')


class Pusher(wxpy.Bot):
    def __init__(self, *args, **kwargs):
        self.client = redis.Redis(settings.REDIS_HOST, db=1)
        self.updated_keys = ''.join(['article_', str(date.today()), '*'])
        super(Pusher, self).__init__(*args, **kwargs)

    # read from redis
    def _has_updated(self):
        if not self.client.keys('article_*'):
            push_logger.error('(╯‵□′)╯︵┻━┻ | There is no article keys!')
            return False
        else:
            if not self.client.keys(self.updated_keys):
                push_logger.info('o(╯□╰)o | No updated articles today!')
                return False
            else:
                push_logger.info('(๑•̀ᄇ•́)و ✧ | Find updated articles today!')
                return True

    def get_updated_articles(self):
        if self._has_updated():
            keys = self.client.keys(self.updated_keys)
            return zip(keys, self.client.mget(keys))
        else:
            return []

    def send_articles(self, pusher):
        update_articles_list = self.get_updated_articles()

    @wxpy.Bot.register(msg_types=wxpy.FRIENDS)
    def auto_accept_friends(self, msg):
        if '天才' in msg.text.lower():
            new_friend = pusher.accept_friend(msg.card)
            new_friend.send_msg('骚年，gay正面吗？滑稽')


if __name__ == '__main__':
    pusher = Pusher()
    template = '(๑•̀ᄇ•́)و ✧ \n{company} 今日更新：\n' \
               '{title} \n 有兴趣不？点此链接 \n {link}\n\n\n'
    update_articles = pusher.get_updated_articles()
    receiver = pusher.search('Aforwardz', sex=wxpy.MALE)[0]
    if not receiver:
        push_logger.error('(╯‵□′)╯︵┻━┻ | Not find the gay!')
    logger = wxpy.get_wechat_logger(receiver)
    logger.info()
    if update_articles:
        for company, articles in update_articles:
            message = ''
            company = company.decode('utf-8')
            articles = eval(articles.decode('utf-8'))
            push_logger.info('the company is: {company}\n'
                             'the article is: {article}\n')
            for title, link in articles.items():
                message += template.format(
                    company=company, title=title, link=link
                )

            receiver.send_msg(message)
    else:
        receiver.send_msg('o(╯□╰)o | 今天木有新东西')
