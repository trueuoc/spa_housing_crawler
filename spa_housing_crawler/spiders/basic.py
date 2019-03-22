# -*- coding: utf-8 -*-
from datetime import datetime
import scrapy

from spa_housing_crawler.items import SpaHousingCrawlerItem


class BasicSpider(scrapy.Spider):
    name = 'basic'
    allowed_domains = ['www.idealista.com']
    start_urls = ['https://www.idealista.com/venta-viviendas/madrid/carabanchel/']

    def parse(self, response):
        default_url = 'http://idealista.com'

        info_flats_xpath = response.xpath("//*[@class='item-info-container']")
        prices_flats_xpath = response.xpath("//*[@class='row price-row clearfix']/span[@class='item-price']/text()")

        links = [str(''.join(default_url + link.xpath('a/@href').extract().pop()))
                 for link in info_flats_xpath]

        prices = [float(flat.extract().replace('.', '').strip())
                  for flat in prices_flats_xpath]

        for flat in zip(links, prices):
                item = SpaHousingCrawlerItem(date=datetime.now().strftime('%Y-%m-%d'), link=flat[0], price=flat[1])
                yield item