# coding: utf-8
import scrapy
from ArticlePusher.util import article_handler
from ArticlePusher.util.utils import PusherGenerator


class BbcSpider(scrapy.Spider):
    name = 'bbc_opera'
    allowed_host = 'bbc.co.uk'
    proxy = True
    start_urls = [
        'http://www.bbc.co.uk/iplayer/categories/drama-and-soaps/all?sort=dateavailable'  # bbc
    ]
    compare_xpath = '//div[@id="category-tleo-list"]'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        if article_handler.article_update(response, self.compare_xpath):
            opera_titles = response.xpath('//div[@class="list-item-inner"]/a/@title').extract()
            opera_links = response.xpath('//div[@class="list-item-inner"]/a/@href').extract()
            assert len(opera_titles) == len(opera_links), '文章标题数与连接数不匹配'
            opera_links = list([response.urljoin(url) for url in opera_links])
            opera_dicts = dict((x, y) for x, y in zip(opera_titles, opera_links))
            bbc = PusherGenerator()
            bbc.save_today_new_articles(self.name, opera_dicts)