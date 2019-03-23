# -*- coding: utf-8 -*-
from datetime import datetime
import scrapy
from spa_housing_crawler.items import House
import re


# -*-   import USER AGENT from settings.py -*-
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

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

    def parse(self, response):
        default_url = 'https://www.idealista.com'

        zone_paths = response.xpath("//div[@class='locations-list clearfix']/ul/li/a/@href").extract()
        zones_links = default_url + zone_paths[17][:-10]  # [17] -> for testing, take only Ceuta
                                                          # [:-10] -> remove "municipios" from path
        # -*- Print Zones -*-
        print_zones = False    # --> True for printing zones (testing)
        if print_zones:
            print("----  ZONES -----")
            for zone in zone_paths:
                print(f"Zone: {zone}")
            print("-----------------------")

        yield response.follow(zones_links, headers= header_UA, callback=self.parse_houses)

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

    def parse_houses(self, response):
        default_url = 'http://idealista.com'

        info_flats_xpath = response.xpath("//*[@class='item-info-container']")
        houses_links.extend([str(''.join(default_url + link.xpath('a/@href')
                                         .extract().pop())) for link in info_flats_xpath])

        # -*- Visit all the pages -*-
        test_onePage = True  # ---> True for visiting only one page (testing)
        if (test_onePage):
            next_page_url = None
        else:
            next_page_url = response.xpath("//a[@class='icon-arrow-right-after']/@href").extract()

        # -*- Visit all the houses of each page -*-
        test_oneHouse = True  # ---> True for visiting only one house (testing)
        if not next_page_url:
            if(test_oneHouse):
                yield response.follow(houses_links[0], headers=header_UA, callback=self.parse_features) # catch one house
            else:
                print(f"{len(houses_links)} houses links catched")
                yield response.follow(houses_links, headers=header_UA, callback=self.parse_features)   # catch all houses
        else:
            yield response.follow(next_page_url[0], headers=header_UA, callback=self.parse_houses)    # catch next page

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

    def parse_features(self, response):
        default_url = 'http://idealista.com/inmuebles'

        house = House()
        house['price'] = response.xpath("//span[@class='txt-bold']/text()").extract()[0]
        house['loc_street'] = response.xpath("//div[@class='clearfix']/ul/li/text()").extract()[0]
        house['loc_city'] = response.xpath("//div[@class='clearfix']/ul/li/text()").extract()[1]
        house['loc_zone'] = response.xpath("//div[@class='clearfix']/ul/li/text()").extract()[2]
        properties = response.xpath("//*[@class='details-property_features']/ul/li/text()").extract()

        house = get_all_properties(house, properties)

        # -*- Print Extracted properties (Raw Text) -*-
        print_properties = True    # --> True for printing extracted properties (testing)
        if print_properties:
            print("----  PROPERTIES -----")
            i = 0
            for prop in properties:
                i += 1
                print(f"{i}. feature: {prop}")
            print("-----------------------")

        # -*- Print Extracted features (Items) -*-
        print_features = True       # --> True for printing extracted features (testing)
        if print_features:
            print("----  ITEM FEATURES -----")
            print(house.values())
            print("-----------------------")

    # ----------------------------------------------------------- #

## ---- *   FUNCTIONS TO EXTRACT FEATURES FROM PROPERTIES  * ----

def get_all_properties(house, properties):
    for prop in properties:
        prop = prop.lower()

        # *-* lift *-*
        match_lift = match_property(prop, ['ascensor'])
        if match_lift:
            house['lift'] = check_property(prop, ['sin','con'])   # 0: no lift ; 1: with lift

        # *-* baths *-*
        match_bath = match_property(prop, ['baño'])
        if match_bath:
            house['bath_num'] = get_number(prop)

    return house

def match_property(property, patterns):
    for pat in patterns:
        match_prop = re.search(pat, property)
        if match_prop != None:
            return True
    return False

def check_property(property, patterns):
    i=0
    for pat in patterns:
        check = re.search(pat, property)
        if(check):
            return i
        i=+1

    print(f"-- no pattern found checking {property} property--")
    return -1

def get_number(property):
    return (re.findall(r'\d+', property)[0])