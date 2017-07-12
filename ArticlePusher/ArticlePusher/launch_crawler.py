# coding: utf-8
import os
from datetime import date
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
import logging

launch_logger = logging.getLogger('launch_logger')


def get_settings():
    settings = get_project_settings()
    LOG_PATH = settings['LOG']
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

    LOG_FILE = os.path.join(LOG_PATH, str(date.today()))
    if not os.path.exists(LOG_FILE):
        f = open(LOG_FILE, 'w')
        f.close()
    settings.set('LOG_FILE', LOG_FILE)
    return settings


def launch_tech_crawler():
    settings = get_settings()
    configure_logging(settings=settings)
    launcher = CrawlerRunner(settings)
    crawlers = launcher.spider_loader.list()
    crawlers = list([c for c in crawlers if c.__contains__('tech')])
    try:
        for crawler in crawlers:
            launcher.crawl(crawler)
        d = launcher.join()
        d.addBoth(lambda _: reactor.stop())
        reactor.run()
        return True
    except Exception as e:
        launch_logger.error('(╯‵□′)╯︵┻━┻ | 爬虫有毛病:\n{excep}'
                            .format(excep=e))
        return False
