# -*- coding: utf-8 -*-
import scrapy
import re
import csv
from datetime import datetime as dt
import time
import sys
import os
from spa_housing_crawler.items import House
import locale

sys.path.append(os.getcwd()+'/spa_housing_crawler')
locale.setlocale(locale.LC_ALL, 'es_ES')

default_url = 'http://idealista.com'
houses_links = []

class HousesSpider(scrapy.Spider):

    def __init__(self, *args, **kwargs):
      super(HousesSpider, self).__init__(*args, **kwargs)

      self.start_urls = [kwargs.get('start_url')]

    name = 'houses'
    allowed_domains = ['idealista.com', 'www.idealista.com/inmueble/']

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

    def parse(self, response):

        d_house = 'https://www.idealista.com/login'     # start-url chosen to indicate we pretend extract denied houses

        # -*- Check if we pretend to extract denied houses -*-
        if self.start_urls[0] == d_house:
            try:
                denied_links=[]
                with open('logHouse.txt') as log:
                    denied_links.extend(log.readlines())
                    denied_links = [s.strip() for s in denied_links]
                try:
                    os.remove('logHouse.txt')
                except Exception as e:
                    print(e)

                for link in denied_links:
                    yield response.follow(link, callback=self.parse_features)

            except Exception as e:
                print(e)

        # -*- Extract houses when regular case (not denied houses) -*-
        else:
            info_flats_xpath = response.xpath("//*[@class='item-info-container']")
            houses_links.extend([str(''.join(default_url + link.xpath('a/@href')
                                             .extract().pop())) for link in info_flats_xpath])

            next_page_url = response.xpath("//a[@class='icon-arrow-right-after']/@href").extract()

            if not next_page_url:
                for house in houses_links:
                    yield response.follow(house, callback=self.parse_features)  # catch houses
            else:
                time.sleep(2)
                yield response.follow(next_page_url[0], callback=self.parse, errback=self.parse_deny)

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

    ''' if a 403 response is received while browsing the pages in the link collection,
            save all the houses stored in 'houses_links' list after quiting '''

    def parse_deny(self, response):
        with open('logHouse.txt', 'a') as log:
            for house in houses_links:
                log.write(house+'\n')

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

    def parse_features(self, response):
        # Set to zero Extra House Equipments
        house = House(
            storage_room=0,
            built_in_wardrobe=0,
            terrace=0,
            balcony=0,
            garden=0,
            chimney=0,
            air_conditioner=0,
            reduced_mobility=0,
            swimming_pool=0,
        )

        # -*- ad description -*-
        try:
            house['ad_description'] = response.xpath("//div[@class='adCommentsLanguage expandable']/text()").extract()
            house['ad_description'][0] = house['ad_description'][0].replace('"', '').strip()
            house['ad_description'][-1] = house['ad_description'][-1].replace('"', '').strip()
        except Exception as e:
            print(e)

        # -*- metadata -*-
        house['ad_last_update'] = (response.xpath("//div[@class='ide-box-detail overlay-box mb-jumbo']/p/text()")
            .extract()[0])
        house['obtention_date'] = dt.now().date()

        # -*- location -*-
        house['loc_full'] = response.xpath("//div[@class='clearfix']/ul/li/text()").extract()
        try:
            house['loc_zone'] = house['loc_full'][-1].strip()
            try:
                house['loc_city'] = house['loc_full'][-2].strip()
                try:
                    house['loc_district'] = house['loc_full'][-3].strip()
                    try:
                        house['loc_neigh'] = house['loc_full'][-4].strip()
                        try:
                            house['loc_street'] = house['loc_full'][-5].strip()
                        except Exception as e:
                            print(e)
                    except Exception as e:
                        print(e)
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)

        # -*- some features -*-
        house['price'] = int(response.xpath("//span[@class='txt-bold']/text()").extract()[0].replace(".", ""))
        house['house_type'] = (response.xpath("//span[@class='main-info__title-main']"
                                              "/text()").extract()[0].split(" en ")[0])
        house['house_id'] = get_number(response.xpath("//ul[@class='lang-selector--lang-options']/li/a/@href")
                                       .extract()[0])

        # -*- house properties from raw text -*-
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

        yield house



    # ----------------------------------------------------------- #
    # ---- *   FUNCTIONS TO EXTRACT FEATURES FROM PROPERTIES  * ----

def get_all_properties(house, properties):
    for prop in properties:
        prop = prop.lower().strip()

        # *-* lift *-*
        if match_property(prop, ['ascensor']):
            house['lift'] = check_property(prop, ['con'])   # 0: no lift ; 1: with lift

        # *-* bath number *-*
        elif match_property(prop, ['baño']):
            try:
                house['bath_num'] = get_number(prop)
            except Exception as e:
                print(e)
                house['bath_num'] = prop

        # *-* construction date *-*
        elif match_property(prop, ['construido en']):
            try:
                house['construct_date'] = get_number(prop)
            except Exception as e:
                print(e)
                house['construct_date'] = prop

        # *-* storage room *-*
        elif match_property(prop, ['trastero']):
            house['storage_room'] = 1           # 0: no storage room ; 1: with storage room

        # *-* orientation of the house *-*
        elif match_property(prop, ['orientación']):
            house['orientation'] = prop.split(' ', maxsplit=1)[1].strip()

        # *-* energetic certification of the house *-*
        elif match_property(prop, ['certific']):
            house['energetic_certif'] = prop.split(':')[1].strip()

        # *-* flat floor *-*
        elif match_property(prop, ['bajo', 'planta', 'interior', 'exterior']):
            house['floor'] = prop

        # *-* room number *-*
        elif match_property(prop, ['habitaci']):
            try:
                house['room_num'] = get_number(prop)
            except:
                house['room_num'] = prop

        # *-* m2 of the house *-*
        elif match_property(prop, ['m²']):
            try:
                house['m2_real'] = get_number(prop.split(',')[0])
                try:
                    house['m2_useful'] = get_number(prop.split(',')[1])
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
                house['m2_real'] = prop

        # *-* condition of the house *-*
        elif match_property(prop, ['segunda mano','promoción de obra nueva']):
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
            house['garage'] = prop

        # *-* heating *-*
        elif match_property(prop, ['calefacción']):
            house['heating'] = prop

        # *-* chimney *-*
        elif match_property(prop, ['chimenea']):
            house['chimney'] = 1

        # *-* ground_size *-*
        elif match_property(prop, ['parcela']):
            try:
                house['ground_size'] = get_number(prop)
            except:
                house['ground_size'] = prop

        # *-* air_conditioner *-*
        elif match_property(prop, ['aire acondicionado']):
            house['air_conditioner'] = 1

        # *-* reduced_mobility *-*
        elif match_property(prop, ['movilidad reducida']):
            house['reduced_mobility'] = 1

        # *-* swimming_pool *-*
        elif match_property(prop, ['piscina']):
            house['swimming_pool'] = 1

        # *-* kitchen & unfurnished *-*
        elif match_property(prop, ['cocina']):
            house['kitchen'] = 1
            if match_property(prop, ['sin amueblar']):
                house['unfurnished'] = 1

        elif match_property(prop, ['sin amueblar']):
            house['unfurnished'] = 1
            if match_property(prop, ['cocina']):
                house['kitchen'] = 1

        # *-* house type redundancy *-*
        elif match_property(prop, ['chalet', 'finca', 'casa', 'caserón', 'palacio']):
            pass

        else:
            # -*- Register undefined properties not included yet -*-
            register_undefined = True  # ---> True for register undefined properties (testing)
            if register_undefined:
                with open('undefined_props.csv', 'a') as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow([prop])
                csvFile.close()

    return house

    # ----------------------------------------------------------- #

def match_property(property, patterns):
    for pat in patterns:
        match_prop = re.search(pat, property)
        if match_prop is not None:
            return True
    return False

def check_property(property, patterns):
    for pat in patterns:
        check = re.search(pat, property)
        if check:
            return 1
    return 0

def get_number(property):
    nums = re.findall(r'\d+', property)
    if len(nums) == 2:
        return int(nums[0]+nums[1])           # '40.000' ->   '40' + '000'  -> '40000'  ->  40000
    else:
        return int(nums[0])