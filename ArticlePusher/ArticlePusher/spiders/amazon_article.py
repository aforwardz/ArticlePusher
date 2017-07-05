# coding: utf-8
import scrapy


class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_host = 'amazon.com'
    start_urls = [
        'https://aws.amazon.com/cn/blogs/aws/'  # amazon
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        print(response.status)
