# -*- coding: utf-8 -*-
import scrapy
from eTechStore.items import UrlItem
import chompjs
import codecs
from urllib.parse import urlencode, urljoin

class NetpunSpider(scrapy.Spider):

    name = 'netpunSpider'
    allowed_domains = ['neptun.mk']
    start_urls = ['https://www.neptun.mk']
    # sitemap_urls = ['https://www.neptun.mk/sitemap.xml']

    custom_settings = {
        # 'JOBDIR': general.get_log_dir(name),
        'ITEM_PIPELINES': {
            'eTechStore.pipelines.UrlManagerPipeline': 300,
        }
    }

    def parse(self, response):

        lst_url = response.xpath("//ul[contains(@class, 'nav navbar-nav')]/li[@id='neptunMain']//a[@target='_self']/@href").getall()
        for link_ in list(set(lst_url)):
            # rel_href = tag_a_.attrib["href"].strip() if "href" in tag_a_.attrib else ""
            if link_:
                this_url = response.request.url
                dict_form_data = {"items": 20, "page": 1}
                href = f"{urljoin(this_url, link_)}?{urlencode(dict_form_data)}"
                yield scrapy.Request(href, callback=self.parse_category_products)


    def parse_category_products(self, response):

        this_url = response.request.url
        base_url = this_url.split('?')[0]

        items_show = 100

        dict_form_data = {}
        dict_form_data['items'] = f'{items_show}'

        new_response = response.replace(encoding='utf-8')
        result = new_response.css('script:contains(shopCategoryModel)::text').get()

        if result:

            decoded = codecs.decode(result, 'unicode_escape').encode('latin1').decode('utf8')
            dict_data = chompjs.parse_js_object(decoded)

            number_of_products = dict_data["NumberOfProducts"]
            page_count = number_of_products // items_show
            page_count = page_count + 1 if number_of_products % items_show else page_count

            lst_links = [f"{base_url}/{dict_product_['Url']}" for dict_product_ in dict_data["Products"]]

            for link_ in lst_links:
                urlItem = UrlItem()
                urlItem["url"] = link_
                yield urlItem

            if page_count > 1:
                for i in range(2, page_count + 1):
                    dict_form_data["page"] = i
                    href = f"{base_url}?{urlencode(dict_form_data)}"
                    yield scrapy.Request(href, callback=self.parse_category_products)