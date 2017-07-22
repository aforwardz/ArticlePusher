import os
from celery.schedules import crontab
from celery import Celery
from kombu import Queue
from datetime import timedelta


app = Celery('ArticlePusher')


class CeleryConfig(object):
    BROKER_URL = 'redis://127.0.0.1:6379/2'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
    CELERY_DEFAULT_QUEUE = 'crawl'
    CELERY_QUEUES = (
        Queue('crawl', routing_key='crawl.#'),
        Queue('push', routing_key='push.#')
    )

    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_IMPORTS = ('ArticlePusher.tasks',)

    CELERYBEAT_SCHEDULE = {
        'crawl_tech_sites': {
            'task': 'ArticlePusher.tasks.crawl_tech_sites',
            'schedule': crontab(minute='50', hour='06'),
        },
        'crawl_opera_sites': {
            'task': 'ArticlePusher.tasks.crawl_opera_sites',
            'schedule': crontab(minute='30', hour='06'),
        },
        # 'push_updates': {
        #     'task': 'tasks.push_new_articles',
        #     'schedule': crontab(
        #         minute='*/30',
        #         hour='8-0',
        #     ),
        # },
    }

app.config_from_object(CeleryConfig)
