import scrapy
from eTechStore.items import ETechStoreItem
import chompjs
import codecs

def parse_product_details_anhoch(response):

    lst_category_path = response.xpath("//div[@id='breadcrumbs']/ul[@class='breadcrumbs']/li//text()").getall()
    lst_category_path = [item_ for item_ in lst_category_path if item_.strip()]
    if lst_category_path:
        lst_category_path = lst_category_path[1:-1]

    product_sel = response.xpath("//section[contains(@class, 'product')]")
    product_name = product_sel.xpath("//div[@class='box-heading ']//h3/text()").get()

    product_info_sec = product_sel.xpath("//section[@class='product-info']")
    price = product_info_sec.xpath("//div[@class='price product-price']//span[@class='nm']/text()").get()
    currency = product_info_sec.xpath("//div[@class='price product-price']//span[@class='sign']/text()").get()
    price = price.replace(",", "") if price else 0.0
    if price and price.isdigit():
        price = float(price)

    lst_desc = product_info_sec.xpath(
        "//div[@class='product-desc']//text()[not(ancestor::div/@class='modal hide fade')][//br]").getall()
    lst_desc = [item_.strip() for item_ in lst_desc if item_.strip()]

    lst_pairs = zip(lst_desc[::2], lst_desc[1::2])
    brand = ""
    code = ""
    for name_, value_ in lst_pairs:
        if name_.startswith("Производител:"):
            brand = value_.strip()
        if name_.startswith("Шифра:"):
            code = value_.strip()
        if name_.startswith("Достапност:"):
            pass

    lst_desc = product_sel.xpath(
        "//div[@class='description']//div[@class='tab-content']//div[@id='description']//div[@class='span8 clearfix']/pre//text()").getall()
    lst_desc = [item_.strip() for item_ in lst_desc if item_.strip()]
    description = "".join(lst_desc)
    description = description.replace("\r", "\n").replace("\n\n", "\n").replace("\t", " ")

    market_name = 'anhoch'

    dict_item = {}
    dict_item["id"] = f'{market_name}-{code}'
    dict_item['brand'] = brand.title()
    dict_item['product_name'] = product_name.strip().replace("Notebook ") if product_name else ""
    dict_item['categories_path'] = lst_category_path
    dict_item['price'] = price
    dict_item['description'] = description
    dict_item['url'] = response.request.url
    dict_item['market_name'] = market_name

    return dict_item

def parse_product_details_neptun(response):

    dict_item = {}

    new_response = response.replace(encoding='utf-8')
    result = new_response.css('script:contains(productModel)::text').get()
    if result:
        decoded = codecs.decode(result, 'unicode_escape').encode('latin1').decode('utf8')
        dict_data = chompjs.parse_js_object(decoded)

        market_name = 'neptun'

        dict_item["id"] = f'{market_name}-{dict_data["Id"]}'
        dict_item['brand'] = dict_data['Manufacturer']['Name'].title()
        dict_item['product_name'] = dict_data['Title'].replace("Лаптоп ", "")
        dict_item['categories_path'] = [data_['Name'] for data_ in dict_data['NavigationPath']]
        dict_item['price'] = dict_data['RegularPrice']
        dict_item['discount_price'] = dict_data['DiscountPrice']
        sel_desc = scrapy.selector.Selector(text=dict_data['Description'])
        lst_desc_line = sel_desc.xpath('//ul/li/text()').getall()
        if lst_desc_line:
            lst_desc_line = [item_.strip() for item_ in lst_desc_line if item_.strip()]

        dict_item['description'] = '\n'.join(lst_desc_line)
        dict_item['url'] = response.request.url
        dict_item['market_name'] = market_name

    return dict_item

def parse_product_details_setec(response):


    product_name = response.xpath("//h1[@id='title-page']/text()").get().strip()
    brand = ""
    description = ""

    lst_category_path = response.xpath("//h1[@id='title-page']/../ul/li/a/text()").getall()
    if product_name in lst_category_path:
        lst_category_path.remove(product_name)

    lst_desc = response.xpath("//div[@class='tab-content']//text()[//br]").getall()
    if lst_desc:
        lst_desc = [item_.strip() for item_ in lst_desc if item_.strip()]
        description = "\n".join(lst_desc)

    lst_desc = response.xpath("//div[@class='description']//text()[//br]").getall()
    lst_desc = [item_.strip() for item_ in lst_desc if item_.strip() and "function(" not in item_.strip()]

    if "Достапност:" in lst_desc:
        lst_desc.remove("Достапност:")

    lst_desc_pair = zip(lst_desc[::2], lst_desc[1::2])
    code = ""

    for name_, value_ in lst_desc_pair:
        if name_.startswith("Бренд:"):
            brand = value_.strip()
        if name_.startswith("Краток опис:"):
            # description = value_
            pass
        if name_.startswith("Шифра:"):
            code = value_.strip()
        if name_.startswith("Гаранција (дена):"):
            pass

    def _get_price_currency(value_str=""):
        price = 0.0
        currency = ""
        if value_str:
            value_str = value_str.strip()
            price_str, currency = value_str.split(" ")
            price_str = price_str.replace(",", "")
            if price_str.isdigit():
                price = float(price_str)

            if currency.endswith("."):
                currency = "".join(currency[:-1])

        return price, currency.lower()


    price_regular = 0.0
    currency = ""
    price_currency_regular = response.xpath("//span[@id='price-old-product']/text()").get()
    if not price_currency_regular:
        price_currency_regular = response.xpath("//div[@id='price-old']/text()").get()
    if price_currency_regular:
        price_regular, currency = _get_price_currency(price_currency_regular)

    price_discount = response.xpath("//span[@id='price-special']/text()").get()
    if price_discount:
        price_discount, _ = _get_price_currency(price_discount)

    if currency.lower() == "ден":
        currency = "МКД"

    market_name = 'setec'

    dict_item = {}
    dict_item["id"] = f'{market_name}-{code}'
    dict_item['brand'] = brand.title()
    dict_item['product_name'] = product_name.strip()
    dict_item['categories_path'] = lst_category_path
    dict_item['price'] = price_regular
    dict_item['discount_price'] = price_discount
    dict_item['description'] = description
    dict_item['url'] = response.request.url
    dict_item['market_name'] = market_name

    return dict_item

class ProductDetailsSpider(scrapy.Spider):

    name = 'productDetailsSpider'
    allowed_domains = ['anhoch.com', 'neptun.mk', 'setec.mk']

    custom_settings = {
        'ITEM_PIPELINES': {
            'eTechStore.pipelines.ElasticSearchPipeline': 400,
        },
        'SPIDER_MIDDLEWARES': {
            'eTechStore.middlewares.ProductDetailsSpiderMiddleware': 543,
        }
    }

    def parse(self, response, **kwargs):
        yield self.parse_product_details(response)

    def parse_product_details(self, response):

        this_url = response.request.url

        eTechStoreItem = ETechStoreItem()

        if "anhoch.com" in this_url:
            eTechStoreItem = parse_product_details_anhoch(response)
        elif "neptun.mk" in this_url:
            eTechStoreItem = parse_product_details_neptun(response)
        elif "setec.mk" in this_url:
            eTechStoreItem = parse_product_details_setec(response)

        return eTechStoreItem