import os

from celery.schedules import crontab
from celery import Celery
# from kombu import Queue
from datetime import timedelta


os.environ.setdefault(
    'ArticlePusher.settings'
)

app = Celery('ArticlePusher')


class CeleryConfig(object):
    broker_url = 'redis://127.0.0.1:6379/2'
    result_backend = 'redis://127.0.0.1:6379/3'
    timezone = 'Asia/Shanghai'

    task_routes = {
        'crawl.tasks.*': {'queue': 'crawl'},
        'push.tasks.*': {'queue': 'push'},
    }

    beat_schedule = {}
    beat_schedule.update({
        'crawl_tech_sites': {
            'task': 'tasks.crawl_tech_sites',
            'schedule': timedelta(seconds=2 * 60),
        },
        'push_updates': {
            'task': 'tasks.push_new_articles',
            'schedule': crontab(
                minute='*/30',
                hour='8-0',
            ),
        },
    })

app.config_from_object(CeleryConfig)
