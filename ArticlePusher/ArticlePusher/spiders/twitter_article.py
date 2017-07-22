# coding: utf-8
import scrapy
from ArticlePusher.util import article_handler
from ArticlePusher.util.utils import PusherGenerator


class TwitterSpider(scrapy.Spider):
    name = 'twitter_tech'
    allowed_host = 'twitter.com'
    proxy = True
    start_urls = [
        'https://blog.twitter.com/engineering/en_us.html'  # twitter
    ]
    compare_xpath = '//div[@class="container--mini container--mobile results-loop   "]'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        if article_handler.article_update(response, self.compare_xpath):
            article_titles = response.xpath('//div[@class="result__copy"]//a/text()').extract()
            article_links = response.xpath('//div[@class="result__copy"]//a/@href').extract()
            assert len(article_titles) == len(article_links), '文章标题数与连接数不匹配'
            article_dicts = dict((x, y) for x, y in zip(article_titles, article_links))
            twitter = PusherGenerator()
            twitter.save_today_new_articles(self.name, article_dicts)
