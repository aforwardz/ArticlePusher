# coding: utf-8
import scrapy
from ArticlePusher.util import article_handler
from ArticlePusher.util.utils import PusherGenerator


class GoogleSpider(scrapy.Spider):
    name = 'google'
    allowed_host = 'googleblog.com'
    start_urls = [
        'https://opensource.googleblog.com/'  # googleblog
    ]
    compare_xpath = '//div[@class="blog-posts hfeed"]'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        if article_handler.article_update(response, self.compare_xpath):
            article_titles = response.xpath('//div[@class="post-outer"]//h3/a/text()').extract()
            article_links = response.xpath('//div[@class="post-outer"]//h3/a/@href').extract()
            article_dicts = dict((x, y) for x, y in zip(article_titles, article_links))
            google = PusherGenerator()
            google.save_today_new_articles(self.name, article_dicts)
