# -*- coding: utf-8 -*-
import scrapy
import sys
import os
from spa_housing_crawler.items import Zone

sys.path.append(os.getcwd()+'/spa_housing_crawler')

# Global declarations
default_url = 'http://idealista.com'
renting = 'https://www.idealista.com/alquiler-viviendas/#municipality-search'
selling_flag = True  # True: Selling ; False: Renting

class GetZones(scrapy.Spider):
    name = 'getZones'
    allowed_domains = ['idealista.com']
    start_urls = ['https://www.idealista.com']

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

    def parse(self, response):
        global selling_flag
        zone_paths = response.xpath("//div[@class='locations-list clearfix']/ul/li/a/@href").extract()

        for path in zone_paths:
            zone = Zone()
            zone['zone'] = (default_url + path)[:-10] + 'mapa'   # [:-10] -> removes 'municipios' from path
            if selling_flag:
                zone['type'] = 'selling'
            else:
                zone['type'] = 'renting'

            yield zone

        if selling_flag:
            selling_flag = False
            yield response.follow(renting, callback=self.parse)