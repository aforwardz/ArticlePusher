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
        self.signature = '\n\n  --该消息来自Aforwardz-Robot'
        self.staff_client = redis.Redis(settings.REDIS_HOST, db=settings.STAFFDB)
        self.util_client = redis.Redis(settings.REDIS_HOST, db=settings.UTILDB)
        self.updated_keys = ''.join(['article_', str(date.today()),'*'])
        super(Pusher, self).__init__(*args, **kwargs)

    # read from redis
    def _has_updated(self):
        if not self.staff_client.keys('article_*'):
            push_logger.error('(╯‵□′)╯︵┻━┻ | 根本没有文章这种东西!')
            return False
        else:
            if not self.staff_client.keys(self.updated_keys):
                push_logger.info('o(╯□╰)o | 今日木有更新!')
                return False
            else:
                push_logger.info('(๑•̀ᄇ•́)و ✧ | 今日有更新!')
                return True

    def _get_updated_articles(self):
        if self._has_updated():
            keys = self.staff_client.keys(self.updated_keys)
            return zip(keys, self.staff_client.mget(keys))
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
        if not self.util_client.exists(group_name):
            push_logger.error(
                '(╯‵□′)╯︵┻━┻ | 根本没有＊{gname}＊这个组!'.format(
                    gname=group_name
                ))
            return
        elif not self.util_client.get(group_name):
            push_logger.info(
                '╮(￣▽￣)╭ | 根本没人对＊{gname}＊这个组感兴趣!'.format(
                    gname=group_name
                ))
            return
        else:
            return eval(self.util_client.get(group_name).decode('utf-8'))

    def _send_staff_to_members(self, members, staff):
        for geek in members:
            try:
                receiver = wxpy.ensure_one(
                    self.search(geek['name'], sex=geek['sex']))
            except ValueError as e:
                push_logger.error(
                    '(╯‵□′)╯︵┻━┻ | {exception}!'.format(exception=e))
                continue

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

                    receiver.send_msg(message+self.signature)
            else:
                receiver.send_msg('╮(￣▽￣)╭ | 今天木有新东西'+self.signature)

    def push_new_staff(self, group_name, test=False):
        if test:
            while True:
                group_members = self._get_group_members(group_name)
                if not group_members:
                    time.sleep(60*60)
                    continue
                update_articles = self._get_updated_articles()
                self._send_staff_to_members(group_members, update_articles)
                time.sleep(60*60)
        else:
            group_members = self._get_group_members(group_name)
            if not group_members:
                return
            update_articles = self._get_updated_articles()
            self._send_staff_to_members(group_members, update_articles)

    # def push_new_staff_to_group_chat(self, group_chat_name, test=False):
    #     group_chat = self.groups().search(keywords=group_chat_name)
    #     if not group_chat:
    #         return
    #     update_articles = self._get_updated_articles()
    #     group_chat.
    #     self._send_staff_to_members(group_members, update_articles)

    def listen_update_flag(self, group_name):
        while True:
            if int(self.util_client.get('update_flag').decode('utf-8')):
                self.push_new_staff(group_name)
                self.util_client.set('update_flag', settings.NO, xx=True)
                time.sleep(60*60)
            else:
                time.sleep(60*60)


if __name__ == '__main__':
    pusher = Pusher(cache_path=True)
    pusher.enable_puid(path='wxpy.pkl')


    @pusher.register(msg_types=wxpy.FRIENDS)
    def auto_accept_friends(msg):
        if '天才' in msg.text.lower():
            new_friend = pusher.accept_friend(msg.card)
            new_friend.send_msg('骚年，gay正面吗？滑稽')


    @pusher.register(msg_types=wxpy.TEXT)
    def add_friend_to_specific_group(msg):
        if 'Aforwardz-Robot' in msg.text:
            push_logger.info('嘿嘿，有银@你！<(￣︶￣)>')
            if 'tech' in msg.text:
                push_group = 'tech_group'
                push_logger.info(
                    '有银想加入{gname}这个组！<(￣︶￣)>'.format(gname=push_group))
                msg.sender.send_msg(
                    '你将被加入{gname}这个组！<(￣︶￣)>'.format(gname=push_group))
            else:
                push_logger.info('介个人只是撩你玩儿╮(╯▽╰)╭')
                msg.sender.send_msg('干嘛！有病吃药！(→_→)')
                return

            if pusher.util_client.exists(push_group):
                push_group_member = pusher.util_client.get(push_group)
                push_group_member = eval(push_group_member.decode('utf-8'))
                if any([msg.sender.nick_name==x['name'] for x in push_group_member]):
                    msg.sender.send_msg(
                        '你已经在{gname}这个组了！<(￣︶￣)>'.format(gname=push_group))
                    return
                push_group_member.append({
                    'name': msg.sender.nick_name,
                    'sex': msg.sender.sex
                })
                pusher.util_client.set(push_group, push_group_member, xx=True)
                msg.sender.send_msg(
                    '你已被加入{gname}这个组！<(￣︶￣)>'.format(gname=push_group))
            else:
                push_group_member = [{
                    'name': msg.sender.nick_name,
                    'sex': msg.sender.sex
                }]
                pusher.util_client.set(push_group, push_group_member)
                push_logger.info('')


    listen_push_thread = threading.Thread(
        target=pusher.listen_update_flag,
        args=['tech_group'],

    )
    listen_push_thread.setDaemon(True)
    listen_push_thread.start()
    pusher.join()
