import scrapy
from spa_housing_crawler import items

class AditionalData(scrapy.Spider):
    name = "getAditionalData"
    start_urls = ['http://www.ine.es/jaxiT3/Datos.htm?t=302', 'http://www.ine.es/jaxiT3/Datos.htm?t=2852']

    def parse(self, response):
        for row in response.xpath('//*[@class="general"]//tbody//tr'):
            info_adicional = items.AditionalDataOjct()
            info_adicional["poblacion"] = row.xpath("th//text()").extract_first()
            info_adicional["valor"] = row.xpath("td[1]//text()").extract_first()
            if response.url == "http://www.ine.es/jaxiT3/Datos.htm?t=302":
                info_adicional["source"] = "Empresas"
            else:
                info_adicional["source"] = "Poblacion"

            yield info_adicional