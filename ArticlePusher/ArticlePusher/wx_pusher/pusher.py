# coding: utf-8
import redis
import wxpy
import threading
import time
from datetime import date
from ArticlePusher import settings
from ArticlePusher.wx_pusher.push_config import PUSH_CONFIG
import logging

push_logger = logging.getLogger('push_logger')


class Pusher(wxpy.Bot):
    def __init__(self, *args, **kwargs):
        self.template = '(๑•̀ᄇ•́)و ✧ \n{company} 今日更新：\n\n' \
                   '{title} \n 有兴趣不？点此链接 \n {link}\n\n'
        self.signature = '\n\n  --该消息来自Aforwardz-Robot'
        self.stuff_client = redis.Redis(settings.REDIS_HOST, db=settings.STUFFDB)
        self.util_client = redis.Redis(settings.REDIS_HOST, db=settings.UTILDB)
        self.updated_keys = ''
        self.manager = {}
        self.set_pusher_manager()
        super(Pusher, self).__init__(*args, **kwargs)

    def set_pusher_manager(self):
        if settings.MANAGER:
            from ArticlePusher.private_settings import MANAGER
            self.manager = MANAGER
            push_logger.info('设置管理员成功')

    def generate_updated_keys(self, subclass, func):
        self.updated_keys = ''.join([subclass, '_', str(date.today()), '*', func])

    # read from redis
    def _has_updated(self, func, subclass):
        if not self.stuff_client.keys(subclass + '*' + func):
            push_logger.error('(╯‵□′)╯︵┻━┻ | 根本没有{stuff_type}这种东西!'.format(
                stuff_type=subclass
            ))
            return False
        else:
            self.generate_updated_keys(subclass, func)
            if not self.stuff_client.keys(self.updated_keys):
                push_logger.info('o(╯□╰)o | 今日木有更新!')
                return False
            else:
                push_logger.info('(๑•̀ᄇ•́)و ✧ | 今日有更新!')
                return True

    def _get_updated_stuff(self, func, subclass):
        if self._has_updated(func, subclass):
            keys = self.stuff_client.keys(self.updated_keys)
            return zip(keys, self.stuff_client.mget(keys))
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
                '(╯‵□′)╯︵┻━┻ | 根本没有＊{name}＊这个组!'.format(
                    name=group_name
                ))
            return
        elif not self.util_client.get(group_name):
            push_logger.info(
                '╮(￣▽￣)╭ | 根本没人对＊{name}＊这个组感兴趣!'.format(
                    name=group_name
                ))
            return
        else:
            return eval(self.util_client.get(group_name).decode('utf-8'))

    def _send_stuff_to_members(self, members, stuff):
        for geek in members:
            try:
                receiver = wxpy.ensure_one(
                    self.friends().search(geek['name'], sex=geek['sex']))
            except ValueError as e:
                push_logger.error(
                    '(╯‵□′)╯︵┻━┻ | {exception}!'.format(exception=e))
                continue

            if stuff:
                for company, articles in stuff:
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

    def _send_stuff_to_group_chat_members(self, chat_members, stuff):
        for group_chat in chat_members:
            try:
                receiver = wxpy.ensure_one(
                    self.groups().search(keywords=group_chat))
            except ValueError as e:
                push_logger.error(
                    '(╯‵□′)╯︵┻━┻ | {exception}!'.format(exception=e))
                continue

            if stuff:
                for company, articles in stuff:
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

    def push_new_stuff(self, func, subclass, group_name, test=False):
        if test:
            while True:
                group_members = self._get_group_members(group_name)
                if not group_members:
                    time.sleep(60*60)
                    continue
                update_stuff = self._get_updated_stuff(func, subclass)
                self._send_stuff_to_members(group_members, update_stuff)
                time.sleep(60*60)
        else:
            group_members = self._get_group_members(group_name)
            if not group_members:
                return

            update_stuff = self._get_updated_stuff(func, subclass)
            self._send_stuff_to_members(group_members, update_stuff)

    def push_new_stuff_to_group_chat(self, func, subclass, group_name):
        group_chats = self._get_group_members(group_name)
        if not group_chats:
            return

        update_stuff = self._get_updated_stuff(func, subclass)
        self._send_stuff_to_group_chat_members(group_chats, update_stuff)

    def add_one_to_one_group(self, one, sex, one_group):
        if self.util_client.exists(one_group):
            push_group_member = self.util_client.get(one_group)
            push_group_member = eval(push_group_member.decode('utf-8'))
            if any([one == x['name'] for x in push_group_member]):
                return False
            push_group_member.append({
                'name': one,
                'sex': sex
            })
            self.util_client.set(one_group, push_group_member, xx=True)
            return True
        else:
            push_group_member = [{
                'name': one,
                'sex': sex
            }]
            self.util_client.set(one_group, push_group_member)
            push_logger.info('')
            return True

    def check_all_push_objects(self):
        for func, sub in PUSH_CONFIG.items():
            update_flag = self.util_client.get(func+'_update')
            if update_flag and update_flag.decode('utf-8'):
                for subclass, (single, groups) in sub.items():
                    self.push_new_stuff(func, subclass, single)
                    self.push_new_stuff_to_group_chat(func, subclass, groups)
                    self.util_client.set(func+'_update', settings.NO, xx=True)
                push_logger.info('%s更新了～' % func)

    def listen_update_flag(self):
        while True:
            self.check_all_push_objects()
            time.sleep(30*60)


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
        if not isinstance(msg.sender, wxpy.Friend):
            return

        if 'Aforwardz-Robot' in msg.text and '加入' in msg.text:
            push_logger.info('嘿嘿，有银@你！还想进组～ <(￣︶￣)>')
            for func, sub in PUSH_CONFIG.items():
                if func in msg.text:
                    for subclass in sub.keys():
                        if subclass in msg.text:
                            add_type = sub[subclass][0]
                            push_logger.info(
                                '有银想加入{name}这个组！<(￣︶￣)>'.format(name=add_type))
                            msg.sender.send_msg(
                                '你将被加入{name}这个组！<(￣︶￣)>'.format(name=add_type))
                        else:
                            continue

                        if pusher.add_one_to_one_group(msg.sender.nick_name,
                                                       msg.sender.sex, add_type):
                            msg.sender.send_msg(
                                '你已被加入{name}这个组！<(￣︶￣)>'.format(name=add_type))
                        else:
                            msg.sender.send_msg(
                                '你已经在{name}这个组了！<(￣︶￣)>'.format(name=add_type))

                else:
                    # push_logger.info('介个人只是撩你玩儿╮(╯▽╰)╭')
                    # msg.sender.send_msg('干嘛！有病吃药！(→_→)')
                    continue

    # 还未有好的方案
    # @pusher.register(msg_types=wxpy.TEXT)
    # def manager_set_things(msg):
    #     if not pusher.manager:
    #         return
    #     if not isinstance(msg.sender, wxpy.Friend):
    #         return
    #     if msg.sender.nick_name == pusher.manager['name'] and \
    #         msg.sender.sex == pusher.manager['sex']:
    #         pass

    listen_push_thread = threading.Thread(
        target=pusher.listen_update_flag,
    )
    listen_push_thread.setDaemon(True)
    listen_push_thread.start()
    pusher.join()
