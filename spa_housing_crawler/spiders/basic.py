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

        # -*- Visit all the houses -*-
        num_houses = 30          # ---> number of houses to catch ; for all -> len(houses_links)
        num_houses = len(houses_links) if num_houses > len(houses_links) else num_houses

        if not next_page_url:
            print(f"----> {len(houses_links)} houses links catched, show just {num_houses}")
            for i in range(num_houses):
                yield response.follow(houses_links[i], headers=header_UA, callback=self.parse_features)  # catch houses
        else:
            yield response.follow(next_page_url[0], headers=header_UA, callback=self.parse_houses)    # catch next page

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

    def parse_features(self, response):
        default_url = 'http://idealista.com/inmuebles'

        # Set to zero Extra House Equipments
        house = House(
            storage_room = 0,
            built_in_wardrobe = 0,
            terrace = 0,
            balcony = 0,
            garden = 0,
            garage = 0,
            chimney = 0,
            air_conditioner = 0,
            reduced_mobility = 0,
            swimming_pool = 0,
        )

        house['price'] = int(response.xpath("//span[@class='txt-bold']/text()").extract()[0].replace(".", ""))
        house['loc_street'] = response.xpath("//div[@class='clearfix']/ul/li/text()").extract()[0].strip()
        house['loc_city'] = response.xpath("//div[@class='clearfix']/ul/li/text()").extract()[1].strip()
        house['loc_zone'] = response.xpath("//div[@class='clearfix']/ul/li/text()").extract()[2].strip()
        properties = response.xpath("//*[@class='details-property_features']/ul/li/text()").extract()

        house = get_all_properties(house, properties)

        # -*- Print Extracted properties (Raw Text) -*-
        print_properties = False    # --> True for printing extracted properties (testing)
        if print_properties:
            print("----  PROPERTIES -----")
            i = 0
            for prop in properties:
                i += 1
                print(f"{i}. feature: {prop}")
            print("-----------------------")

        # -*- Print Extracted features (Items) -*-
        print_features = False       # --> True for printing extracted features (testing)
        if print_features:
            print("----  ITEM FEATURES -----")
            print(house.values())
            print("-----------------------")

    # ----------------------------------------------------------- #


## ---- *   FUNCTIONS TO EXTRACT FEATURES FROM PROPERTIES  * ----

def get_all_properties(house, properties):
    for prop in properties:
        prop = prop.lower().strip()

        # *-* lift *-*
        if match_property(prop, ['ascensor']):
            house['lift'] = check_property(prop, ['con'])   # 0: no lift ; 1: with lift

        # *-* bath number *-*
        elif match_property(prop, ['baño']):
            house['bath_num'] = get_number(prop)

        # *-* construction date *-*
        elif match_property(prop, ['construido en']):
            house['construct_date'] = get_number(prop)

        # *-* storage room *-*
        elif match_property(prop, ['trastero']):
            house['storage_room'] = 1           # 0: no storage room ; 1: with storage room

        # *-* orientation of the house *-*
        elif match_property(prop, ['orientación']):
            house['orientation'] = prop.split(' ',maxsplit=1)[1].strip()

        # *-* energetic certification of the house *-*
        elif match_property(prop, ['certific']):
            house['energetic_certif'] = prop.split(':')[1].strip()

        # *-* flat floor *-*
        elif match_property(prop, ['bajo','planta']):
            house['floor'] = prop

        # *-* room number *-*
        elif match_property(prop, ['habitaci']):
            house['room_num'] = get_number(prop)

        # *-* m2 of the house *-*
        elif match_property(prop, ['m²']):
            house['m2_real'] = get_number(prop.split(',')[0])

            try:
                house['m2_useful'] = get_number(prop.split(',')[1])
            except:
                pass

        # *-* condition of the house *-*
        elif match_property(prop, ['segunda mano']):
            house['condition'] = prop

        # *-* built in wardrobe *-*
        elif match_property(prop, ['armarios empotrados']):
            house['built_in_wardrobe'] = 1

        # *-* terrace *-*f
        elif match_property(prop, ['terraza']):
            house['terrace'] = 1

        # *-* balcony *-*
        elif match_property(prop, ['balcón']):
            house['balcony'] = 1

        # *-* garden *-*
        elif match_property(prop, ['jardín']):
            house['garden'] = 1

        # *-* garage *-*
        elif match_property(prop, ['garaje']):
            house['garage'] = 1

        # *-* house type *-*
        elif match_property(prop, ['chalet', 'finca', 'casa']):
            house['house_type'] = prop

        # *-* heating *-*
        elif match_property(prop, ['calefacción']):
            house['heating'] = prop

        # *-* chimney *-*
        elif match_property(prop, ['chimenea']):
            house['chimney'] = prop

        # *-* ground_size *-*
        elif match_property(prop, ['parcela']):
            house['ground_size'] = get_number(prop)

        # *-* air_conditioner *-*
        elif match_property(prop, ['aire acondicionado']):
            house['air_conditioner'] = 1

        # *-* reduced_mobility *-*
        elif match_property(prop, ['movilidad reducida']):
            house['reduced_mobility'] = 1

        # *-* swimming_pool *-*
        elif match_property(prop, ['piscina']):
            house['swimming_pool'] = 1

        else:
            print("--  --  --  --  --  ")
            print(f"property not included yet: {prop}")
            print("--  --  --  --  --  ")

    return house

    # ----------------------------------------------------------- #


def match_property(property, patterns):
    for pat in patterns:
        match_prop = re.search(pat, property)
        if match_prop != None:
            return True
    return False

def check_property(property, patterns):
    for pat in patterns:
        check = re.search(pat, property)
        if(check):
            return 1
    return 0

def get_number(property):
    nums = re.findall(r'\d+', property)

    if len(nums)==2:
        return(int(nums[0]+nums[1]))            # '40.000' ->   '40' + '000'  -> '40000'  ->  40000
    else:
        return int(nums[0])