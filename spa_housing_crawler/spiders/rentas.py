import scrapy
from spa_housing_crawler import items

class AditionalData(scrapy.Spider):
    name = "renta"
    start_urls = ['https://www.agenciatributaria.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfCodPostal/2016/jrubikf15b9305df2e5d53b0bbd20afaea102233fc84fd9.html']

    def parse(self, response):
        for row in response.xpath('//*[@id="table01"]//tbody//tr'):
            renta = items.Renta()
            renta["poblacion"] = row.xpath("th//text()").extract_first()
            renta["n_declaraciones"] = row.xpath("td[1]//text()").extract_first()
            renta["renta_bruta_media"] = row.xpath("td[1]//text()").extract_first()
            renta["renta_disponible_media"] = row.xpath("td[1]//text()").extract_first()
            renta["renta_de_trabajos"] = row.xpath("td[1]//text()").extract_first()
            renta["rentas_exentas"] = row.xpath("td[1]//text()").extract_first()
            renta["renta_bruta"] = row.xpath("td[1]//text()").extract_first()
            renta["cotizaciones_ss"] = row.xpath("td[1]//text()").extract_first()
            renta["cuota_rentable"] = row.xpath("td[1]//text()").extract_first()
            renta["renta_disponible"] = row.xpath("td[1]//text()").extract_first()


            yield renta