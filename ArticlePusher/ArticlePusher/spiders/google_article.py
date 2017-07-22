# coding: utf-8
import scrapy
from ArticlePusher.util import article_handler
from ArticlePusher.util.utils import PusherGenerator


class GoogleSpider(scrapy.Spider):
    name = 'google_tech'
    allowed_host = 'googleblog.com'
    proxy = True
    start_urls = [
        'https://opensource.googleblog.com/'  # google open source blog
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
            assert len(article_titles) == len(article_links), '文章标题数与连接数不匹配'
            article_dicts = dict((x, y) for x, y in zip(article_titles, article_links))
            google = PusherGenerator()
            google.save_today_new_articles(self.name, article_dicts)
