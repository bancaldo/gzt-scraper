import json
import scrapy


class NamesSpider(scrapy.Spider):
    name = "names"
    allowed_domains = ["Gazzetta.it"]

    def start_requests(self):
        urls = ["http://www.Gazzetta.it/calcio/fantanews/statistiche/serie-a-2017-18/",]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for url in response.css('td.field-giocatore a::attr(href)').extract():
            if url:
                name_code = url.split('/')[-1]
                yield {'player': name_code,
                       }
