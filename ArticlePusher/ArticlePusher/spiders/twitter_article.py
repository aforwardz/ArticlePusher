# coding: utf-8
import scrapy


class TwitterSpider(scrapy.Spider):
    name = 'twitter'
    allowed_host = 'twitter.com'
    start_urls = [
        'https://blog.twitter.com/engineering/en_us.html'  # twitter
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        print(response.status)
