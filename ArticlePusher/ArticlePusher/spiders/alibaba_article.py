# coding: utf-8
import scrapy
from ArticlePusher.util import article_handler
from ArticlePusher.util.utils import PusherGenerator


class AlibabaSpider(scrapy.Spider):
    name = 'alibaba_tech'
    allowed_host = 'taobao.org'
    proxy = False
    start_urls = [
        'http://jm.taobao.org/'  # alibaba middleware
    ]
    compare_xpath = '//section[@id="posts"]'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        if article_handler.article_update(response, self.compare_xpath):
            article_titles = response.xpath('//a[@class="post-title-link"]/text()').extract()
            article_titles = list([x.replace('\n', '').replace(' ', '') for x in article_titles])
            article_links = response.xpath('//a[@class="post-title-link"]/@href').extract()
            article_links = list([response.urljoin(x) for x in article_links])
            assert len(article_titles) == len(article_links), '文章标题数与连接数不匹配'
            article_dicts = dict((x, y) for x, y in zip(article_titles, article_links))
            alibaba = PusherGenerator()
            alibaba.save_today_new_articles('article', self.name, article_dicts)
