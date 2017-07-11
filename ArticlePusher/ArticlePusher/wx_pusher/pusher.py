# coding: utf-8
import redis
import wxpy
import threading
import time
from datetime import date
from ArticlePusher import settings
import logging

push_logger = logging.getLogger('push_logger')


class Pusher(wxpy.Bot):
    def __init__(self, *args, **kwargs):
        self.template = '(๑•̀ᄇ•́)و ✧ \n{company} 今日更新：\n' \
                   '{title} \n 有兴趣不？点此链接 \n {link}\n\n\n'
        self.client = redis.Redis(settings.REDIS_HOST, db=1)
        self.updated_keys = ''.join(['article_', str(date.today()),'*'])
        super(Pusher, self).__init__(*args, **kwargs)

    # read from redis
    def _has_updated(self):
        if not self.client.keys('article_*'):
            push_logger.error('(╯‵□′)╯︵┻━┻ | 根本没有文章这种东西!')
            return False
        else:
            if not self.client.keys(self.updated_keys):
                push_logger.info('o(╯□╰)o | 今日木有更新!')
                return False
            else:
                push_logger.info('(๑•̀ᄇ•́)و ✧ | 今日有更新!')
                return True

    def _get_updated_articles(self):
        if self._has_updated():
            keys = self.client.keys(self.updated_keys)
            return zip(keys, self.client.mget(keys))
        else:
            return []

    # def _auto_accept_friends(self, msg):
    #     if '天才' in msg.text.lower():
    #         new_friend = self.accept_friend(msg.card)
    #         new_friend.send_msg('骚年，gay正面吗？滑稽')
    #
    # def _add_friend_to_specific_group(self, msg):
    #     if msg.text.__contains__('Aforwardz-Robot'):
    #         if msg.text.__contains__('tech'):
    #             push_group = 'tech_group'
    #         else:
    #             return
    #
    #         if self.client.exists(push_group):
    #             push_group_member = self.client.get(push_group)
    #             push_group_member.append({
    #                 'name': msg.sender.nick_name,
    #                 'sex': msg.sender.sex
    #             })
    #             self.client.set(push_group, push_group_member, xx=True)
    #         else:
    #             push_group_member = [{
    #                 'name': msg.sender.nick_name,
    #                 'sex': msg.sender.sex
    #             }]
    #             self.client.set(push_group, push_group_member)
    #             push_logger.info('')

    def _get_group_members(self, group_name):
        if not self.client.exists(group_name):
            push_logger.error(
                '(╯‵□′)╯︵┻━┻ | 根本没有＊{gname}＊这个组!'.format(
                    gname=group_name
                ))
            return
        elif not self.client.get(group_name):
            push_logger.info(
                'o(╯□╰)o | 根本没人对＊{gname}＊这个组感兴趣!'.format(
                    gname=group_name
                ))
            return
        else:
            return self.client.get(group_name)

    def _send_staff_to_members(self, members, staff):
        for geek in members:
            try:
                receiver = wxpy.ensure_one(
                    self.search(geek['name'], sex=geek['sex']))
            except ValueError as e:
                push_logger.error(
                    '(╯‵□′)╯︵┻━┻ | {exception}!'.format(
                        exception=e
                    ))
                continue
            # logger = wxpy.get_wechat_logger(receiver)
            # logger.info()
            if staff:
                for company, articles in staff:
                    message = ''
                    company = company.decode('utf-8')
                    articles = eval(articles.decode('utf-8'))
                    push_logger.info('大牛公司: {company}\n'
                                     '更新了: {article}\n')
                    for title, link in articles.items():
                        message += self.template.format(
                            company=company, title=title, link=link
                        )

                    receiver.send_msg(message)
            else:
                receiver.send_msg('o(╯□╰)o | 今天木有新东西')

    def push_new_staff(self, group_name, test=False):
        if test:
            while True:
                group_members = self._get_group_members(group_name)
                if not group_members:
                    time.sleep(30)
                    continue
                update_articles = self._get_updated_articles()
                self._send_staff_to_members(group_members, update_articles)
                time.sleep(30)
        else:
            group_members = self._get_group_members(group_name)
            update_articles = self._get_updated_articles()
            self._send_staff_to_members(group_members, update_articles)


pusher = Pusher(cache_path=True)


@pusher.register(msg_types=wxpy.FRIENDS)
def auto_accept_friends(self, msg):
    if '天才' in msg.text.lower():
        new_friend = self.accept_friend(msg.card)
        new_friend.send_msg('骚年，gay正面吗？滑稽')


@pusher.register(msg_types=wxpy.TEXT)
def add_friend_to_specific_group(self, msg):
    if msg.text.__contains__('Aforwardz-Robot'):
        if msg.text.__contains__('tech'):
            push_group = 'tech_group'
        else:
            return

        if self.client.exists(push_group):
            push_group_member = self.client.get(push_group)
            push_group_member.append({
                'name': msg.sender.nick_name,
                'sex': msg.sender.sex
            })
            self.client.set(push_group, push_group_member, xx=True)
        else:
            push_group_member = [{
                'name': msg.sender.nick_name,
                'sex': msg.sender.sex
            }]
            self.client.set(push_group, push_group_member)
            push_logger.info('')

listen_push_thread = threading.Thread(
    target=pusher.push_new_staff,
    args=['tech_group', True]
)
listen_push_thread.setDaemon(True)
listen_push_thread.start()
pusher.join()
