# import json
import scrapy
from gazzetta.items import PlayerItem


class GazzettaSpider(scrapy.Spider):
    name = "gazzetta"
    allowed_domains = ["gazzetta.it"]

    def __init__(self, day='', *args, **kwargs):
        super(GazzettaSpider, self).__init__(*args, **kwargs)
        self.day = day

    def start_requests(self):
        urls = ["http://www.gazzetta.it/calcio/fantanews/"
                "statistiche/serie-a-2017-18/", ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # day = raw_input("***[INFO] Insert day to scrap: ")
        for url in response.css('td.field-giocatore a::attr(href)').extract():
            if url:
                player_item = PlayerItem()
                # player_item assignments
                player_item['link'] = url
                player_item['day'] = self.day.strip()
                yield response.follow(url, callback=self.parse_player,
                                      meta={'player_item': player_item})

    @staticmethod
    def parse_player(response):
        def extract_with_css(query, ev_day):
            return [q.css(query).extract_first()
                    for q in response.css('li.day-%s' % ev_day)][0]
        error_file = open("ERROR.txt", "w")
        player_item = response.meta.get('player_item')
        day = player_item.get('day')
        link = player_item.get('link')
        name = response.css('h1 a::text').extract_first().strip()
        name_code = link.split('/')[-1]
        code = name_code.split('_')[-1]
        team = response.css(
            'div.category-title-column a::attr(href)').extract_first()
        try:
            yield {'code': code,
                   'name': name,
                   'team': team,
                   'ruolo': extract_with_css('span.field-role::text', day),
                   'fv': extract_with_css('span.field-fv::text', day),
                   'v': extract_with_css('span.field-v::text', day),
                   'gol': extract_with_css('span.field-g::text', day).strip(),
                   'q': response.css('span.field-q::text').extract()[1],
                   'link': link,
                   }
        except IndexError:
            print "ERROR: No data for ", link
            error_file.write("No data for %s" % link)
        error_file.close()
