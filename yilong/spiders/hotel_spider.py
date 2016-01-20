# -*- coding: utf-8 -*-
from scrapy.spider import Spider,Rule
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from yilong.items import hotelItem

class hotelSpider(Spider):

    #we can input what kind of hotel you like for searching
    searchItem = raw_input("Please input what you want to search?")
 #   searchItem = "五星级"
    print searchItem

    
    #append all of the link into links
    links = []

    #name of spider
    name = "hotel"
    start_urls = ["http://hotel.elong.com/search/list_cn_0101.html?Keywords="+searchItem+"&KeywordsType=999&aioIndex=-1&aioVal="+searchItem]
                
#    rules = (
#            Rule(SgmlLinkExtractor(restrict_xpaths=('/html/body/div[2]/div[5]/div[1]/div[5]/div/div[@class="h_item"]/div/div[2]/div[3]//p[@class="h_info_b1]'))
#                                   ,callback='parse_eachHotel')
#        )

    #initialize once the spider start.
    def __init__(self):
        self.browser = webdriver.Firefox()

    #done once the spider finished.
    def __del__(self):
        self.browser.close()

    #after __init__(), the spider goes from here.
    def parse(self,response):
        
        #use browser to open link: response.url in this case, the url is start_url
        self.browser.get(response.url)

        #after open successfully, load the whole page source
        sel = Selector(text = self.browser.page_source)

        #I did not a little bit research, in this elong.com. all of the page of item(navigation for direct pages)
        #have the exact same xpath, and also the last second one is the biggest number of page.
        #So we can use this feature to find out how many pages in total
        urls = sel.xpath('/html/body/div[2]/div[5]/div[1]/div[6]/a/text()').extract()

        #pages in total
        total_page = urls[len(urls)-2]
        page_count = 1

        while True:
            
            #find the "go to next page" button, and click it go to next page

            #right here we only consider the first three pages

            #if page_count < total_page
            if page_count < 2:

                #find the button,
                button = self.browser.find_element_by_xpath('/html/body/div[2]/div[5]/div[1]/div[6]/a[@class="page_next"]')                                              

                #after open successfully, load the whole page source
                sel = Selector(text = self.browser.page_source)
    
                # start to do the jobs.
                datas = sel.xpath('/html/body/div[2]/div[5]/div[1]/div[5]/div/div[@class="h_item"]/div/div[2]/div[3]//p[@class="h_info_b1"]')
                prices = sel.xpath('/html/body/div[2]/div[5]/div[1]/div[5]/div/div[@class="h_item"]/div/div[2]/div[@class="h_info_pri"]/p/a')
            
                
                count = 0
                for data in datas:
           
                    link = data.xpath('a/@href').extract()
                    print 'http://hotel.elong.com'+link[0],count
                    self.links.append('http://hotel.elong.com'+link[0])
                #from there we extract all of the sublink from the start url
                #and pass it to a new parse function to extract the real data
                    count += 1

                #simulate browser action - click
                button.click()

                #sleep for a while and waiting for ajax refresh
                time.sleep(5)
                
                page_count += 1
 
            else:
                sel = Selector(text = self.browser.page_source)
                datas = sel.xpath('/html/body/div[2]/div[5]/div[1]/div[5]/div/div[@class="h_item"]/div/div[2]/div[3]//p[@class="h_info_b1"]')
                prices = sel.xpath('/html/body/div[2]/div[5]/div[1]/div[5]/div/div[@class="h_item"]/div/div[2]/div[@class="h_info_pri"]/p/a')


                count = 0
                for data in datas:
                    link = data.xpath('a/@href').extract()
                    print 'http://hotel.elong.com'+link[0],count
                    self.links.append('http://hotel.elong.com' + link[0])
                    count += 1
                break

        #now we have stored all of the hotel link from each page.
        #just need to yield all of the links to do further jobs.
        for temp in self.links:
            yield Request(url = temp,callback= self.parse_eachHotel)
            


    #the request from the parse(), will call this function.
    def parse_eachHotel(self,response):
        download_delay = 2
        #let javascript load
        self.browser.get(response.url)
        
        sel = Selector(text=self.browser.page_source)
        print sel

        #since there are two different xpath for webpage.
        #so we check the first extraction from xpath
        #default is that the name in the top
        names = sel.xpath('/html/body/div[3]/div/div[1]/div[@class="hdetail_main hrela_name"]')
        data_1 = sel.xpath('/html/body/div[4]/div/div[1]/div[4]/div/div/div[@class="htype_item on"]')
        hdata_1 = sel.xpath('/html/body/div[4]/div[1]/div[1]/div[4]/div/div[@class="htype_list"]/div[@class="htype_item on"]/div[@class="htype_info_list btddd"]')
        
        #if the extraction is empty;
        if not names:
            #we used the other xpath for extracting data.
            #name in the side
           namesNew = sel.xpath('/html/body/div[3]/div/div[1]/div[2]/div[1]/div[1]/div[@class="hrela_name left"]/div[1]')                              
           name = namesNew[0].xpath('h1/text()').extract()
           data_2 = sel.xpath('/html/body/div[4]/div/div[1]/div[1]/div[3]/div/div[@class="htype_list"]/div[@class="htype_item on"]')
           hdata_2 = sel.xpath('/html/body/div[4]/div/div[1]/div[1]/div[3]/div/div[@class="htype_list"]/div[@class="htype_item on"]/div[@class="htype_info_list"]')
           datas =  data_2
           hdatas = hdata_2
        else:
           name = names[0].xpath('div[@class="t24 yahei"]/@title').extract()
           datas = data_1
           hdatas = hdata_1
           
        items = []
        count = 0
        for data in datas:
            item = hotelItem()
            
            htype = data.xpath('div[@class="htype_info clearfix"]/div[@class="htype_info_nt"]/p[@class="htype_info_name"]/span/text()').extract()
            hprice = data.xpath('div[@class="htype_info clearfix"]/div[@class="htype_info_pb right"]/p[@class="cf55"]/span[@class="htype_info_num"]/text()').extract()
            ht_name = hdatas[count].xpath('table[@class="htype-table"]/tbody/tr/td[@class="ht_name"]/span/text()').extract()
            ht_price = hdatas[count].xpath('table[@class="htype-table"]/tbody/tr/td[@class="ht_pri"]/span[@class="ht_pri_h cur"]/span[@class="ht_pri_num"]/text()').extract()

            item["ht_name"] = ht_name
            item["ht_price"] = ht_price
            item["name"] = name
            item["htype"] = htype
            item["hprice"] = hprice
            item["link"] = 1

            count += 1
            items.append(item)
        return items
            
                          
