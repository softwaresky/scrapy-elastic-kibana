import scrapy
from eTechStore.items import ETechStoreItem, UrlItem
from scrapy.crawler import CrawlerProcess
from eTechStore import general
import pprint

class SetecSpider(scrapy.Spider):

    name = 'setecSpider'
    allowed_domains = ['setec.mk']
    start_urls = ['https://setec.mk']

    custom_settings = {
        # 'JOBDIR': general.get_log_dir(name),
        'ITEM_PIPELINES': {
            'eTechStore.pipelines.UrlManagerPipeline': 300,
        }
    }

    def parse(self, response):

        lst_url = response.xpath("//div[@class='megamenu-wrapper']//ul[@class='megamenu fade']//li//a[@class='main-menu ']/@href").getall()
        for href_ in list(set(lst_url)):
            if href_:
                yield scrapy.Request(href_, callback=self.parse_category_products)

    def parse_category_products(self, response):

        lst_url = response.xpath("//div[contains(@class, 'product ')]//a/@href").getall()
        for url_ in list(set(lst_url)):
            urlItem = UrlItem()
            urlItem["url"] = url_
            yield urlItem

        for tag_a_ in response.xpath("//ul[@class='pagination']/li/a"):
            href = tag_a_.attrib["href"] if "href" in tag_a_.attrib else ""
            if href and tag_a_.xpath("./text()").get() == ">":
                yield scrapy.Request(href, callback=self.parse_category_products)

# if __name__ == "__main__":
#     process =  CrawlerProcess()
#     process.crawl(SetecSpider)
#     process.start()