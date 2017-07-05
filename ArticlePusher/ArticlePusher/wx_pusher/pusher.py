# coding: utf-8
import redis
import wxpy
from datetime import datetime
from ArticlePusher import settings
import logging

push_logger = logging.getLogger('push_logger')


class Pusher(wxpy.Bot):
    def __init__(self, *args, **kwargs):
        self.client = redis.Redis(settings.REDIS_HOST)
        self.updated_keys = 'article_' + str(datetime.date()) + '*'
        super(Pusher, self).__init__(*args, **kwargs)

    # read from redis
    def _has_updated(self):
        if not self.client.exists('article_*'):
            push_logger.error('(╯‵□′)╯︵┻━┻ | There is no article keys!')
            return False
        else:
            if not self.client.exists(self.updated_keys):
                push_logger.info('o(╯□╰)o | No updated articles today!')
                return False
            else:
                push_logger.info('(๑•̀ᄇ•́)و ✧ | Find updated articles today!')
                return True

    def get_updated_articles(self):
        if self._has_updated():
            keys = self.client.keys(self.updated_keys)
            return self.client.mget(keys)
        else:
            return []

    def send_articles(self, pusher):
        update_articles_list = self.get_updated_articles()


def run():
    pusher = Pusher()
    update_articles_list = pusher.get_updated_articles()
    receiver = pusher.search('Aforwardz', sex=wxpy.MALE)[0]
    if len(update_articles_list) > 0:
        for article in update_articles_list:
            receiver.send(article)
