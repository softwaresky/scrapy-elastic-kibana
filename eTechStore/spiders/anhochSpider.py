import scrapy
from eTechStore.items import UrlItem

class AnhochSpider(scrapy.Spider):

    name = 'anhochSpider'
    allowed_domains = ['anhoch.com']
    start_urls = ['https://www.anhoch.com']

    custom_settings = {
        # 'JOBDIR': general.get_log_dir(name),
        'ITEM_PIPELINES': {
            'eTechStore.pipelines.UrlManagerPipeline': 300,
        }
    }

    def parse(self, response):

        lst_url = response.xpath("//div[@id='categories_collapse']//a/@href").getall()
        count = response.meta.get("cookiejar", 0)
        for href_ in list(set(lst_url)):
            if href_:
                yield scrapy.Request(href_, callback=self.parse_category_products)


    def parse_category_products(self, response):

        lst_url = response.xpath("//div[@class='products']/ul[contains(@class, 'products')]/li//div[contains(@class, 'product-name')]//a/@href").getall()

        for url_ in list(set(lst_url)):
            urlItem = UrlItem()
            urlItem["url"] = url_
            yield urlItem

        next_url = response.xpath("//div[contains(@class, 'pagination')]/ul/li//i[@class='icon-angle-right']/../@href").get()
        if next_url:
            yield  scrapy.Request(next_url, callback=self.parse_category_products)