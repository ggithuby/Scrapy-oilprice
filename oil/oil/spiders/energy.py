# -*- coding:utf-8 -*-
import scrapy
import logging
from ..items import OilItem
import time

logger=logging.getLogger(__name__)

class EnergySpider(scrapy.Spider):
    name = "energy"
    # custom_settings = {
    #     # 设置log日志
    #     'LOG_LEVEL': 'INFO',
    #     'LOG_FILE': 'E:\oilprice\ENERGY.log'
    # }
    # start_urls = ["https://oilprice.com/Energy/Heating-Oil/",
    #               "https://oilprice.com/Energy/Gas-Prices/",
    #               "https://oilprice.com/Energy/Natural-Gas",
    #               "https://oilprice.com/Energy/Coal/"]
                    #"https://oilprice.com/Energy/Energy-General/","https://oilprice.com/Energy/Oil-Prices/","https://oilprice.com/Energy/Crude-Oil/",
    def __init__(self):
        self.count = 0

    def start_requests(self):
        urls = ["https://oilprice.com/Energy/Heating-Oil/",
                "https://oilprice.com/Energy/Gas-Prices/",
                "https://oilprice.com/Energy/Natural-Gas",
                "https://oilprice.com/Energy/Coal/"]
        for url in urls:
            yield scrapy.Request(url=url,callback=self.parse)

    def parse(self, response):
        for i in range(1,12):#中间有个广告，被ABP屏蔽不显示，但占位置
            xpath_ad='//*[@id="pagecontent"]/div[3]/div/div[1]/div['+str(i)+']/div[1]/text()'
            ad=response.selector.xpath(xpath_ad).extract()
            if ad and ad[0]=='Sponsored Article':
                # print(ad)
                pass
            else:
                xpath_url='//*[@id="pagecontent"]/div[3]/div/div[1]/div['+str(i)+']/a/@href'
                url=response.selector.xpath(xpath_url).extract()
                if url:
                    yield scrapy.Request(url=url[0],callback=self.parse_url)
        xpath_next = '//*[@id="pagecontent"]/div[3]/div/div[1]/div[12]/a[11]/@href'
        next = response.selector.xpath(xpath_next).extract()
        if not next:
            xpath_next = '//*[@id="pagecontent"]/div[3]/div/div[1]/div[12]/a[9]/@href'
            next = response.selector.xpath(xpath_next).extract()
        # self.count+=1
        next=response.selector.xpath(xpath_next).extract()
        if next:
            next=next[0]
            yield scrapy.Request(url=next,callback=self.parse)
            print("next page:", next)

    def parse_url(self, response):
        url=response.url
        # print("    ",url)
        item = OilItem()
        xpath_title='//*[@id="singleArticle__content"]/h1/text()'
        title=response.selector.xpath(xpath_title).extract()
        title=''.join(title)
        xpath_text='//*[@id="article-content"]/p/text()'
        text=response.selector.xpath(xpath_text).extract()
        text=''.join(text)
        xpath_time='//*[@id="singleArticle__content"]/span/text()'
        time = response.selector.xpath(xpath_time).extract()
        time=''.join(time)
        if time:
            try:
                time=time[6:-4]
            except:
                time=time
        # print("    ",time)
        item['url'] = url
        item['title'] = title
        item['text'] = text
        item['time'] = time
        try:
            item['type']=url.split('/')[4]#'Oil-Prices'#'Energy-General'
        except:
            item['type'] =''
        yield item