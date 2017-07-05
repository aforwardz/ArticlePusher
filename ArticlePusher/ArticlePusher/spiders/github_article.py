# coding: utf-8
import scrapy


class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_host = 'githubengineering.com'
    start_urls = [
        'https://githubengineering.com/'  # githubengineering
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        print(response.status)
