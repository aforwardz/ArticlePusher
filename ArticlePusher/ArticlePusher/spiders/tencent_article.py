# coding: utf-8
import scrapy
from ArticlePusher.util import article_handler
from ArticlePusher.util.utils import PusherGenerator


class TencentSpider(scrapy.Spider):
    name = 'tencent_tech'
    allowed_host = 'tencentdba.com'
    proxy = False
    start_urls = [
        'http://tencentdba.com/'  # tencent
    ]
    compare_xpath = '//div[@class="primary-site"]'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        if article_handler.article_update(response, self.compare_xpath):
            article_titles = response.xpath('//div[@class="primary-site"]//h2[@class="entry-title"]/a/text()').extract()
            article_links = response.xpath('//div[@class="primary-site"]//h2[@class="entry-title"]/a/@href').extract()
            assert len(article_titles) == len(article_links), '文章标题数与连接数不匹配'
            article_dicts = dict((x, y) for x, y in zip(article_titles, article_links))
            amazon = PusherGenerator()
            amazon.save_today_new_articles('article', self.name, article_dicts)
