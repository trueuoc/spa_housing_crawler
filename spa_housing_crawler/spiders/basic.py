# -*- coding: utf-8 -*-
from datetime import datetime
import scrapy
from spa_housing_crawler.items import SpaHousingCrawlerItem

# -*---    import USER AGENT from settings.py
import sys, os
sys.path.append(os.getcwd()+'/spa_housing_crawler')
from settings import USER_AGENT
header_UA = {'User-Agent': USER_AGENT}

houses_links = []

class BasicSpider(scrapy.Spider):
    name = 'basic'
    allowed_domains = ['idealista.com',
                       'www.idealista.com/inmueble/']


    start_urls = ['https://www.idealista.com/venta-viviendas/#municipality-search/']        # --> house selling
    # start_urls = ['https://www.idealista.com/alquiler-viviendas/#municipality-search/']   # --> house renting

    def parse(self, response):
        default_url = 'https://www.idealista.com'

        zone_paths = response.xpath("//div[@class='locations-list clearfix']/ul/li/a/@href").extract()
        zones_links = default_url + zone_paths[17][:-10]  # [17] -> for testing, take only Ceuta
                                                          # [:-10] -> remove "municipios" from path

        #for zone in zone_paths:
        #    print(f"Zonas: {zone}")

        yield response.follow(zones_links, headers= header_UA, callback=self.parse_houses)

    def parse_houses(self, response):
        default_url = 'http://idealista.com'

        info_flats_xpath = response.xpath("//*[@class='item-info-container']")
        houses_links.extend([str(''.join(default_url + link.xpath('a/@href').extract().pop())) for link in info_flats_xpath])

        next_page_url = response.xpath("//a[@class='icon-arrow-right-after']/@href").extract()

        if not next_page_url:
            print(f"{len(houses_links)} houses links catched")
            house_link = houses_links[0]  # [0] ---> for testing, take only first

            yield response.follow(house_link, headers=header_UA, callback=self.parse_features)       #  catch features

        else:
            yield response.follow(next_page_url[0], headers=header_UA, callback=self.parse_houses)   #  catch next page

    def parse_features(self, response):
        default_url = 'http://idealista.com/inmuebles'
        price = response.xpath("//span[@class='txt-bold']/text()").extract()[0]
        properties = response.xpath("//*[@class='details-property_features']/ul/li/text()").extract()

        loc_street = response.xpath("//div[@class='clearfix']/ul/li/text()").extract()[0]
        loc_city = response.xpath("//div[@class='clearfix']/ul/li/text()").extract()[1]
        loc_zone = response.xpath("//div[@class='clearfix']/ul/li/text()").extract()[2]

        print(f"precio: {price}")
        print(f"calle: {loc_street}")
        print(f"ciudad: {loc_city}")
        print(f"zona: {loc_zone}")

        i=0
        for prop in properties:
            i+=1
            print(f"{i}. característica: {prop}")