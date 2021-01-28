import scrapy
import time
import datetime
import sqlite3
import os
import re

from newscrawling.items import NewscrawlingItem
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import DropItem
from twisted.internet.error import TimeoutError, TCPTimedOutError
from dateutil.parser import parse
from pyvirtualdisplay import Display

display = Display(visible=0, size=(1920,1080))
display.start()

path_webdriver = "/chromedriver"

def save_pdf(response):
    path = response.url.split('/')[-1]
    url = response.url
    url = exchanger(url)

    conn = sqlite3.connect("tender.db")
    cur = conn.cursor()

    idSql = """SELECT id FROM 'tender' where documents like '%{0}%'""".format(url)
    countSql = """update tender set Qty_DownDoc = Qty_DownDoc + 1 where Documents like '%{0}%'""".format(url)
    checkSql = """select Qty_TotalDoc, Qty_DownDoc from tender where Documents like '%{0}%'""".format(url)
    updateSql = """update tender set Down_Status = '{0}' where Documents like '%{1}%'"""

    cur.execute(idSql)
    dbId = cur.fetchall()
    dbId = str(dbId[0][0])

    if not os.path.isdir("/srv1/process/Files/{0}".format(dbId)):
        os.mkdir("/srv1/process/Files/{0}".format(dbId))
        
    with open('Files/' + dbId + '/' + path, 'wb') as f:
        f.write(response.body)
  
    cur.execute(countSql)
    conn.commit()
    cur.execute(checkSql)
     
    fetch = cur.fetchall()
    print(fetch)
    
    if fetch[0][0] == fetch[0][1]:
        cur.execute(updateSql.format('o', url))
        conn.commit()
    else:
        cur.execute(updateSql.format('x', url))
        conn.commit()  

def dbCheck(item):
    conn = sqlite3.connect("tender.db")
    cur = conn.cursor()
    selectSql =  """select * from tender where 
                    Documents like '%{0}%' and
                    Bid_IssuanceTime like '%{1}%' and
                    Bid_OpenTime like '%{2}%'
                    """.format(item['Documents'], item['Bid_IssuanceTime'], item['Bid_OpenTime'])
    cur.execute(selectSql) 

    return cur.fetchall()

def exchanger(pdf):
    if type(pdf) is str:
        pdf = pdf.replace("'","[apos]")
        pdf = pdf.replace('"','[quot]')
        pdf = pdf.replace(',','[comma]')
        pdf = pdf.replace(' ','$20')
        return pdf
    if type(pdf) is list:
        pdfs=[]
        for a in pdf:
            a = a.replace("'","[apos]")
            a = a.replace('"','[quot]')
            a = a.replace(',','[comma]')   
            a = a.replace(' ','$20')
            pdfs.append(a)  
        return pdfs



class ASPOWER(scrapy.Spider):
    name = "ASPOWER"
    allowed_domains = ["www.aspower.com"]
    start_urls = ["https://www.aspower.com/aspa-procurement-01.html"]
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }
    fileDown = 0
    count = 0
    
    def __init__(self):
        scrapy.Spider.__init__(self)
        self.browser = webdriver.Chrome(path_webdriver)
        self.All_TotalDoc = 0

    def parse(self, response):
        if type(response) == 'str':
            self.browser.get(response)
        else:
            self.browser.get(response.url)  
        time.sleep(5)

        html = self.browser.find_element_by_xpath('//*').get_attribute('outerHTML')
        selector = Selector(text=html)

        rows = selector.xpath('//*[@id="welcome"]/div[1]/table/tbody/tr')
        length = len(rows)
        nextPage = selector.xpath('//*[@id="welcome"]/div[1]/table/tbody/tr[{0}]/td[2]/div/a/@href'.format(length))[0].extract()

        item = NewscrawlingItem()

        for i, row in enumerate(rows):
            if i == length - 1 :
                break
  
            td1 = row.xpath('./td[1]/p/span/strong/a/@href')

            urls = []
            if "pdf" in response.urljoin(td1[0].extract()):
                urls.append(response.urljoin(td1[0].extract()).replace(" ","%20"))
            if row.xpath('./td[2]/span/a/@href').extract():
                for i in row.xpath('./td[2]/span/a/@href').extract():
                    if "pdf" in response.urljoin(i):
                        urls.append(response.urljoin(i).replace(" ","%20"))

            documents = ','.join(exchanger(urls))
      
            issuanceTime= row.xpath('./td[2]/span/text()')[0].extract()
            issuanceTime = re.sub('[-=+,#/\?^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', issuanceTime)
            dueDate = row.xpath('./td[2]/span/text()')[1].extract()
            dueDate = dueDate.split('A.Samoa')[0]
            dueDate = re.sub('[-=+,#/\?^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', dueDate)



            item['Company'] = "ASPOWER"
            item['Documents'] = documents
            item["Bid_Descriptions"] = ""
            try:
                item['Bid_IssuanceTime'] = str(parse(issuanceTime))
            except:
                item['Bid_IssuanceTime'] = ""
            try:
                item['Bid_OpenTime'] = str(parse(openTime))
            except:
                item['Bid_OpenTime'] = ""
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = len(urls)
            item['Qty_DownDoc'] = 0

            fetchall = dbCheck(item)
            if  fetchall:
                pass
            else:
                yield item
                for file_url in urls:
                    yield scrapy.Request(
                        url= file_url,
                        callback=save_pdf,
                        dont_filter=True,
                    )  


        # if self.count == 3:
        #     pass
        # else:
        #     if nextPage == 'aspa-procurement-01.html':
        #         return
        #     else:    
        #         yield scrapy.Request("https://www.aspower.com/" + nextPage, self.parse)          

class ESCOM(scrapy.Spider):
    name = "ESCOM"
    allowed_domains = ["www.escom.mw"]
    start_urls = ["http://www.escom.mw/tender-documents.php"]
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.count = 0

    def parse(self, response):

        rows = response.xpath('//*[@id="table1"]/tbody/tr')
        item = NewscrawlingItem()

        for row in rows:
            href = row.xpath('td[2]/a/@href').extract()
            documents = []
            file_urls = []
            openTime = row.xpath('td[4]/text()').get()

            for url in href:
                url = response.urljoin(url)
                file_urls.append(url)
                url = exchanger(url)
                documents.append(url)

            item['Company'] = "ESCOM"
            item['Documents'] = ','.join(documents)
            item["Bid_Descriptions"] = ""
            item['Bid_IssuanceTime'] = ''
            try:
                item['Bid_OpenTime'] = str(parse(openTime))
            except:
                item['Bid_OpenTime'] = ""
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = 1
            item['Qty_DownDoc'] = 0

            fetchall = dbCheck(item)
            if self.count == 10:
                break
            else:
                self.count += 1
                if  fetchall:
                    pass
                else:
                    yield item
                    for file_url in file_urls:
                        yield scrapy.Request(
                            url= file_url,
                            callback=save_pdf,
                            dont_filter=True,
                        )  

class UMEME(scrapy.Spider):
    name = "UMEME"
    allowed_domains = ["www.umeme.co.ug"]
    start_urls = ["https://www.umeme.co.ug/tenders"]
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.browser = webdriver.Chrome(path_webdriver)

    def parse(self, response):
        self.browser.get(response.url)
        time.sleep(5)  

        html = self.browser.find_element_by_xpath('//*').get_attribute('outerHTML')
        selector = Selector(text=html)

        rows = selector.xpath('//*[@id="root"]/div[1]/div[1]/div[2]/div[7]/table/tbody/tr')
        item = NewscrawlingItem()

        for row in rows:
            href = row.xpath('td[4]/a/@href').extract()
            documents = []
            file_urls = []
            openTime = row.xpath('td[3]/text()').get()

            for url in href:
                url = response.urljoin(url)
                file_urls.append(url)
                url = exchanger(url)
                documents.append(url)

            item['Company'] = "UMEME"
            item['Documents'] = ','.join(documents)
            item["Bid_Descriptions"] = ""
            item['Bid_IssuanceTime'] = ''
            try:
                item['Bid_OpenTime'] = str(parse(openTime))
            except:
                item['Bid_OpenTime'] = ""
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = 1
            item['Qty_DownDoc'] = 0

            fetchall = dbCheck(item)
            if  fetchall:
                pass
            else:
                yield item
                for file_url in file_urls:
                    yield scrapy.Request(
                        url= file_url,
                        callback=save_pdf,
                        dont_filter=True,
                    )  

class GUAM(scrapy.Spider):
    name = 'GUAM'
    allowed_domains = ["www.guampowerauthority.com"]
    start_urls = ['http://guampowerauthority.com/gpa_authority/procurement/gpa_current_rfps.php']
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.count = 0

    def parse(self, response):
        item = NewscrawlingItem()
        rows = response.xpath('//tr[@class="bodycopygrey" and position() > 1]')

        for row in rows:
            href=row.xpath('./td[2]/p/a/@href | ./td[2]/p/@href | ./td[2]/p/span/span/a/@href | ./td[2]/p/span/a/@href | ./td[2]/p/span/@href').extract()
            description = row.xpath('./td[2]/p/text() | ./td[2]/p/strong/text() | ./td[2]/p/p/text() | ./td[2]/p/span/text()').getall()
            issuanceTime = row.xpath('./td[4]/div/text() | ./td[4]/div/span/text()').get()
            openTime = str(row.xpath('./td[5]/div/p[1]/text()').get()) + str(row.xpath('./td[5]/div/p[2]/text()').get())
            print(openTime)
            documents =[]
            file_urls =[]

            for url in href:
                url = response.urljoin(url)
                file_urls.append(url)
                url = exchanger(url)
                documents.append(url)

            item["Company"] = "GUAM"
            item["Documents"] = ','.join(documents)
            item["Bid_Descriptions"] = ','.join(description)
            try:
                item["Bid_IssuanceTime"] = str(parse(issuanceTime))
            except:
                item["Bid_IssuanceTime"] = ""
            try:
                item["Bid_OpenTime"] = str(parse(openTime))
            except:
                item["Bid_OpenTime"] = ""               
            item['InputTime'] = datetime.datetime.now()
            item["Down_Status"] = 'x'
            item["Qty_TotalDoc"] = len(documents)
            item["Qty_DownDoc"] = 0

            fetchall = dbCheck(item)
            if  fetchall:
                pass
            else:
                yield item
                for file_url in file_urls:
                    yield scrapy.Request(
                        url= file_url,
                        callback=save_pdf,
                        dont_filter=True,
                    )

class HESCO(scrapy.Spider):
    name = 'HESCO'
    allowed_domains=["www.hesco.gov.pk"]
    start_urls = ['http://www.hesco.gov.pk/NewsMedia.asp?type=02']
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.count = 0 
        
    def parse(self, response):
        item = NewscrawlingItem()
        rows = response.xpath('/html/body/div/div[2]/div[2]/table/tbody/tr')

        for row in rows:
            href = row.xpath('./td[3]/a/@href').extract()
            description = row.xpath('./td[2]/text()').extract()
            issuanceTime = row.xpath('./td[1]/text()')[0].extract()
            documents = []
            file_urls = []

            for url in href:
                url = response.urljoin(url)
                file_urls.append(url)
                url = exchanger(url)
                documents.append(url)

            item["Company"] = "HESCO"
            item["Documents"]= ','.join(documents)
            item["Bid_Descriptions"] = ','.join(description)
            try:
                item['Bid_IssuanceTime'] = str(parse(issuanceTime))
            except:
                item['Bid_IssuanceTime'] = ""
            item['Bid_OpenTime'] = ""
            item["InputTime"] = datetime.datetime.now()
            item["Down_Status"] = 'x'
            item["Qty_TotalDoc"] = len(documents)
            item["Qty_DownDoc"] = 0

            fetchall = dbCheck(item)
            if self.count == 20:
                break
            else:
                self.count += 1
                if  fetchall:
                    pass
                else:
                    yield item
                    for file_url in file_urls:
                        yield scrapy.Request(
                            url= file_url,
                            callback=save_pdf,
                            dont_filter=True,
                        )  

class KENYA(scrapy.Spider):
    name = 'KENYA'
    # allowed_domains=["www.kplc.co.ke"]
    start_urls = ['https://kplc.co.ke/category/view/41/tender-documents? page=1']
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }
    def __init__(self):
        scrapy.Spider.__init__(self)
        self.count = 0

    def start_requests(self):
        page_nums=2
        for page_num in range(1, page_nums):
            yield scrapy.Request("https://kplc.co.ke/category/view/41/tender-documents?page={0}".format(page_num), callback=self.parse_pages)

    def parse_pages(self, response):
        rows = response.xpath('//*[@id="content"]/div[2]/div/div')
        for row in rows:
            yield scrapy.Request(row.xpath('.//h2/a/@href')[0].extract(), callback=self.parse_url)

    def parse_url(self, response):
        item = NewscrawlingItem()
        hrefs = []
        for href in response.xpath('//*[@id="content"]/div[2]/article/div/div[2]/a'):
            hrefs.append(href.xpath('.//@href')[0].extract())
        documents = []
        file_urls = []

        for url in hrefs:
            url = response.urljoin(url)
            file_urls.append(url)
            url = exchanger(url)
            documents.append(url)
   
        item["Company"] = "KENYA"
        item["Documents"]= ','.join(documents)
        item["Bid_Descriptions"] = ""
        item["Bid_IssuanceTime"] = ""
        item['Bid_OpenTime'] = ""
        item["InputTime"] = datetime.datetime.now()
        item["Down_Status"] = 'x'
        item["Qty_TotalDoc"] = len(documents)
        item["Qty_DownDoc"] = 0

        fetchall = dbCheck(item)
        if  fetchall:
            pass
        else:
            yield item 
            for file_url in file_urls:
                yield scrapy.Request(
                    url= file_url,
                    callback=save_pdf,
                    dont_filter=True,
                )   

class MOEE(scrapy.Spider):
    name = 'MOEE'
    allowed_domains=["www.moee.gov.mm"]
    start_urls = ['http://www.moee.gov.mm/en/ignite/page/62']
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }
    def __init__(self):
        scrapy.Spider.__init__(self)

    def start_requests(self):
        last_page = 20
        for page_num in range(0, last_page, 5):
            yield scrapy.Request("http://www.moee.gov.mm/en/ignite/page/62/{0}".format(page_num), callback=self.parse_pages)

    def parse_pages(self, response):
        rows = response.xpath('//*[@id="loading"]/div[5]/div/div[2]/div/div')
        for row in rows:
            yield scrapy.Request(response.urljoin(row.xpath('./div[1]/div[2]/a/@href').get()), callback=self.parse_url)

    def parse_url(self, response):
        item = NewscrawlingItem()
        href = response.xpath('//*[@id="loading"]/div[5]/div/div[2]/div[1]/div[1]/div/a/@href').extract()
        documents = []
        file_urls = []
        description = response.xpath('//*[@id="loading"]/div[5]/div/div[2]/div[1]/div[1]/p/text()').get()

        for url in href:
            url = response.urljoin(url)
            file_urls.append(url)
            url = exchanger(url)
            documents.append(url)
   
        item["Company"] = "MOEE"
        item["Documents"]= ','.join(documents)
        item["Bid_Descriptions"] = description
        item["Bid_IssuanceTime"] = ""
        item['Bid_OpenTime'] = ""
        item["InputTime"] = datetime.datetime.now()
        item["Down_Status"] = 'x'
        item["Qty_TotalDoc"] = len(documents)
        item["Qty_DownDoc"] = 0

        fetchall = dbCheck(item)
        if  fetchall:
            pass
        else:
            yield item
            for file_url in file_urls:
                yield scrapy.Request(
                    url= file_url,
                    callback=save_pdf,
                    dont_filter=True,
                )   

class NPC(scrapy.Spider):
    name = 'NPC'
    # allowed_domains=["www.napocor.gov.ph"]
    start_urls = ['https://www.napocor.gov.ph/BCSD/bids.php']
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }        

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.browser = webdriver.Chrome(path_webdriver)
        self.ids_seen = set()
        self.count = 0

    def parse(self, response):
        self.browser.get(response.url)
        time.sleep(5)  

        html = self.browser.find_element_by_xpath('//*').get_attribute('outerHTML')
        selector = Selector(text=html)

        rows = selector.xpath('//div[@class="modal fade"]')
        for row in rows:
            item = NewscrawlingItem()
            href = row.xpath('./div/div/div[2]/div/div[10]/div[2]/a/@href').extract()
            documents = []
            file_urls = []
            description = row.xpath('./div/div/div[2]/div/div[6]/div[2]/text()').get()
            issuanceTime = str(row.xpath('./div/div/div[2]/div/div[7]/div[2]/text()[2]').get()) + " " + str(row.xpath('./div/div/div[2]/div/div[7]/div[2]/text()[3]').get())
            openTime = row.xpath('./div/div/div[2]/div/div[9]/div[2]/text()[2]').get() + " " + row.xpath('./div/div/div[2]/div/div[9]/div[2]/text()[3]').get()
            for url in href:
                url = response.urljoin(url)
                file_urls.append(url)
                url = exchanger(url)
                documents.append(url)
            item['Company'] = "NPC"
            item['Documents'] = ','.join(documents)
            item["Bid_Descriptions"] = description
            try:
                item['Bid_IssuanceTime'] = str(parse(issuanceTime))
            except:
                item['Bid_IssuanceTime'] = ""
            try:
                item['Bid_OpenTime'] = str(parse(openTime))
            except:
                item['Bid_OpenTime'] = ""
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = len(documents)
            item['Qty_DownDoc'] = 0

            fetchall = dbCheck(item)
            if self.count == 80:
                break
            else:
                self.count += 1
                if  fetchall:
                    pass
                else:
                    yield item
                    for file_url in file_urls:
                        yield scrapy.Request(
                            url= file_url,
                            callback=save_pdf,
                            dont_filter=True,
                        )   

####

class APSCL(scrapy.Spider):
    name = "APSCL"
    allowed_domains = ["www.apscl.gov.bd"]
    start_urls = ['http://www.apscl.gov.bd/site/view/tenders_type/%E0%A6%87-%E0%A6%9C%E0%A6%BF%E0%A6%AA%E0%A6%BF//-']
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }    

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.browser = webdriver.Chrome(path_webdriver)

    def parse(self, response):
        self.browser.get(response.url)
        time.sleep(5)  

        html = self.browser.find_element_by_xpath('//*').get_attribute('outerHTML')
        selector = Selector(text=html)

        rows = selector.xpath('//*[@id="example"]/tbody/tr')
        for row in rows:
            item = NewscrawlingItem()
            hrefs = []
            for href in row.xpath('./td[6]/div/a'):
                hrefs.append(href.xpath('.//@href')[0].extract())
            documents = []
            file_urls = []
            description = row.xpath('./td[2]/text()')[0].extract()
            issuanceTime = row.xpath('./td[4]/text()').get()
            openTime = row.xpath('./td[5]/text()').get()
            for url in hrefs:
                url = response.urljoin(url)
                file_urls.append(url)
                url = exchanger(url)
                documents.append(url)
            item['Company'] = "APSCL"
            item['Documents'] = ','.join(documents)
            item["Bid_Descriptions"] = ""
            try:
                item['Bid_IssuanceTime'] = str(parse(issuanceTime))
            except:
                item['Bid_IssuanceTime'] = ""
            try:
                item['Bid_OpenTime'] = str(parse(openTime))
            except:
                item['Bid_OpenTime'] = "" 
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = len(documents)
            item['Qty_DownDoc'] = 0

            fetchall = dbCheck(item)
            if  fetchall:
                pass
            else:
                yield item
                for file_url in file_urls:
                    yield scrapy.Request(
                        url= file_url,
                        callback=save_pdf,
                        dont_filter=True,
                    )   

class DPDC(scrapy.Spider):
    name = "dpdc"
    allowed_domains = ["www.dpdc.org.bd"]
    start_urls = ['https://www.dpdc.org.bd/page/view/36']
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }    

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.browser = webdriver.Chrome(path_webdriver)

    def parse(self, response):
        self.browser.get(response.url)
        time.sleep(5)  

        html = self.browser.find_element_by_xpath('//*').get_attribute('outerHTML')
        selector = Selector(text=html)

        rows = selector.xpath('//*[@id="page-datasource-holder"]/div/div[2]/table/tbody/tr')

        for row in rows:
            item = NewscrawlingItem()
            href = row.xpath('./td[5]/a/@href').extract()
            documents = []
            file_urls = []
            description = row.xpath('./td[2]/text()')[0].extract()
            issuanceTime = row.xpath('./td[3]/text()').get()
            openTime = row.xpath('./td[4]/text()').get()
            for url in href:
                url = response.urljoin(url)
                file_urls.append(url)
                url = exchanger(url)
                documents.append(url)

            item['Company'] = "DPDC"
            item['Documents'] = ','.join(documents)
            item["Bid_Descriptions"] = description
            try:
                item['Bid_IssuanceTime'] = str(parse(issuanceTime))
            except:
                item['Bid_IssuanceTime'] = ""
            try:
                item['Bid_OpenTime'] = str(parse(openTime))
            except:
                item['Bid_OpenTime'] = "" 
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = len(documents)
            item['Qty_DownDoc'] = 0

            fetchall = dbCheck(item)
            if  fetchall:
                pass
            else:
                yield item
                for file_url in file_urls:
                    yield scrapy.Request(
                        url= file_url,
                        callback=save_pdf,
                        dont_filter=True,
                    )    

class BREB(scrapy.Spider):#일부날짜안됨 접속안됨
    name = "BREB"
    allowed_domains = ["www.reb.gov.bd"]
    start_urls = ['http://www.reb.gov.bd/site/page/0db00bbf-1697-4a4e-8935-73d78c84094b']
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }    

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.browser = webdriver.Chrome(path_webdriver)
        self.count = 0

    def parse(self, response):
        self.browser.get(response.url)
        time.sleep(5)  

        html = self.browser.find_element_by_xpath('//*').get_attribute('outerHTML')
        selector = Selector(text=html)

        rows=selector.xpath('//*[@id="printable_area"]/div/table[1]/thead/tr')

        for row in rows[1:]:
            item = NewscrawlingItem()
            href = row.xpath('./td[5]/a/@href').extract()
            documents = []
            file_urls = []
            description = row.xpath('./td[2]/text()')[0].extract()
            issuanceTime = row.xpath('./td[3]/text()').get()
            openTime = row.xpath('./td[4]/text()').get()
            for url in href:
                url = response.urljoin(url)
                file_urls.append(url)
                url = exchanger(url)
                documents.append(url)

            item['Company'] = "BREB"
            item['Documents'] = ','.join(documents)
            item["Bid_Descriptions"] = description
            try:
                item['Bid_IssuanceTime'] = str(parse(issuanceTime))
            except:
                item['Bid_IssuanceTime'] = ""
            try:
                item['Bid_OpenTime'] = str(parse(openTime))
            except:
                item['Bid_OpenTime'] = ""         
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = len(documents)
            item['Qty_DownDoc'] = 0

            fetchall = dbCheck(item)
            if self.count == 20:
                break
            else :
                if  fetchall:
                    pass
                else:
                    self.count += 1
                    yield item
                    for file_url in file_urls:
                        yield scrapy.Request(
                            url= file_url,
                            callback=save_pdf,
                            dont_filter=True,
                        )  

class PBS(scrapy.Spider):#접속안됨
    name = "PBS"
    allowed_domains = ["www.reb.gov.bd"]
    start_urls = ['http://www.reb.gov.bd/site/page/d41ba549-d6f1-4ec5-9630-bcfe32e61d46/-']
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }    

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.browser = webdriver.Chrome(path_webdriver)
        self.count = 0

    def parse(self, response):
        self.browser.get(response.url)
        time.sleep(5)  

        html = self.browser.find_element_by_xpath('//*').get_attribute('outerHTML')
        selector = Selector(text=html)

        rows=selector.xpath('//*[@id="printable_area"]/div/table/tbody/tr')
        for row in rows[1:]:
            item = NewscrawlingItem()
            hrefs = []
            for href in row.xpath('./td[4]/a | ./th[4]/a'):
                hrefs.append(href.xpath('.//@href')[0].extract())
            documents = []
            file_urls = []
            description = row.xpath('./th[2]//text() | ./td[2]//text()').extract()
            issuanceTime = row.xpath('./th[3]//text() | ./td[3]//text()').get()
            for url in hrefs:
                url = response.urljoin(url)
                file_urls.append(url)
                url = exchanger(url)
                documents.append(url)

            item['Company'] = "PBS"
            item['Documents'] = ','.join(documents)
            item["Bid_Descriptions"] = ' '.join(description)
            try:
                item['Bid_IssuanceTime'] = str(parse(issuanceTime))
            except:
                item['Bid_IssuanceTime'] = ""  
            item['Bid_OpenTime'] = ''
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = len(documents)
            item['Qty_DownDoc'] = 0
            
            fetchall = dbCheck(item)    
            if self.count == 20:
                break
            else :
                if  fetchall:
                    pass
                else:
                    self.count += 1
                    yield item
                    for file_url in file_urls:
                        yield scrapy.Request(
                            url= file_url,
                            callback=save_pdf,
                            dont_filter=True,
                        )  

class WZPDCL_local(scrapy.Spider):#일부날짜안됨 접속안됨
    name = "WZPDCL_local"
    allowed_domains = ["www.wzpdcl.org.bd"]
    start_urls = ['http://www.wzpdcl.org.bd/site/view/tenders_type/স্থানীয়/-']
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }    

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.browser = webdriver.Chrome(path_webdriver)

    def parse(self, response):
        self.browser.get(response.url)
        time.sleep(5)  

        html = self.browser.find_element_by_xpath('//*').get_attribute('outerHTML')
        selector = Selector(text=html)

        rows = selector.xpath('//*[@id="example"]/tbody/tr')
        for row in rows:
            item = NewscrawlingItem()
            href = row.xpath('./td[6]/div/a/@href').extract()
            documents = []
            file_urls = []
            description = row.xpath('./td[2]/text()')[0].extract()
            issuanceTime = row.xpath('./td[4]/text()').get()
            openTime = row.xpath('./td[5]/text()').get()
            for url in href:
                url = response.urljoin(url)
                file_urls.append(url)
                url = exchanger(url)
                documents.append(url)

            item['Company'] = "WZPDCL_local"
            item['Documents'] = ','.join(documents)
            item["Bid_Descriptions"] = description
            try:
                item['Bid_IssuanceTime'] = str(parse(issuanceTime))
            except:
                item['Bid_IssuanceTime'] = ""
            try:
                item['Bid_OpenTime'] = str(parse(openTime))
            except:
                item['Bid_OpenTime'] = "" 
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = len(documents)
            item['Qty_DownDoc'] = 0

            fetchall = dbCheck(item)
            if  fetchall:
                pass
            else:
                yield item
                for file_url in file_urls:
                    yield scrapy.Request(
                        url= file_url,
                        callback=save_pdf,
                        dont_filter=True,
                    )  

class WZPDCL_international(scrapy.Spider):#일부날짜안됨 접속안됨
    name = "WZPDCL_international"
    allowed_domains = ["www.wzpdcl.org.bd"]
    start_urls = ['http://www.wzpdcl.org.bd/site/view/tenders_type/আন্তর্জাতিক/-']
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }    

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.browser = webdriver.Chrome(path_webdriver)

    def parse(self, response):
        self.browser.get(response.url)
        time.sleep(5)  

        html = self.browser.find_element_by_xpath('//*').get_attribute('outerHTML')
        selector = Selector(text=html)

        rows = selector.xpath('//*[@id="example"]/tbody/tr')
        for row in rows:
            item = NewscrawlingItem()
            hrefs = []
            for href in row.xpath('./td[6]/div/a'):
                hrefs.append(href.xpath('.//@href')[0].extract())
            documents = []
            file_urls = []
            description = row.xpath('./td[2]/text()')[0].extract()
            issuanceTime = row.xpath('./td[4]/text()').get()
            openTime = row.xpath('./td[5]/text()').get()
            for url in hrefs:
                url = response.urljoin(url)
                file_urls.append(url)
                url = exchanger(url)
                documents.append(url)

            item['Company'] = "WZPDCL_international"
            item['Documents'] = ','.join(documents)
            item["Bid_Descriptions"] = description
            try:
                item['Bid_IssuanceTime'] = str(parse(issuanceTime))
            except:
                item['Bid_IssuanceTime'] = ""
            try:
                item['Bid_OpenTime'] = str(parse(openTime))
            except:
                item['Bid_OpenTime'] = "" 
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = len(documents)
            item['Qty_DownDoc'] = 0

            fetchall = dbCheck(item)
            if  fetchall:
                pass
            else:
                yield item
                for file_url in file_urls:
                    yield scrapy.Request(
                        url= file_url,
                        callback=save_pdf,
                        dont_filter=True,
                    )  

class NESCO_LOCAL(scrapy.Spider):#일부날짜안됨
    name = "NESCO_LOCAL"
    allowed_domains = ["www.nesco.gov.bd"]
    start_urls = ['http://nesco.gov.bd/site/view/tenders_type/%E0%A6%B8%E0%A7%8D%E0%A6%A5%E0%A6%BE%E0%A6%A8%E0%A7%80%E0%A7%9F/-']
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }    

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.browser = webdriver.Chrome(path_webdriver)

    def parse(self, response):
        self.browser.get(response.url)
        time.sleep(5)  

        html = self.browser.find_element_by_xpath('//*').get_attribute('outerHTML')
        selector = Selector(text=html)

        rows = selector.xpath('//*[@id="example"]/tbody/tr')
        for row in rows:
            item = NewscrawlingItem()
            hrefs = []
            for href in row.xpath('./td[6]/div/a'):
                hrefs.append(href.xpath('.//@href')[0].extract())
            documents = []
            file_urls = []
            description = row.xpath('./td[2]/text()')[0].extract()
            issuanceTime = row.xpath('./td[4]/text()').get()
            openTime = row.xpath('./td[5]/text()').get()
            for url in hrefs:
                url = response.urljoin(url)
                file_urls.append(url)
                url = exchanger(url)
                documents.append(url)
            item['Company'] = "NESCO_LOCAL"
            item['Documents'] = ','.join(documents)
            item["Bid_Descriptions"] = ""
            try:
                item['Bid_IssuanceTime'] = str(parse(issuanceTime))
            except:
                item['Bid_IssuanceTime'] = ""
            try:
                item['Bid_OpenTime'] = str(parse(openTime))
            except:
                item['Bid_OpenTime'] = "" 
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = len(documents)
            item['Qty_DownDoc'] = 0

            fetchall = dbCheck(item)
            if  fetchall:
                pass
            else:
                yield item
                for file_url in file_urls:
                    yield scrapy.Request(
                        url= file_url,
                        callback=save_pdf,
                        dont_filter=True,
                    )  

class NESCO_international(scrapy.Spider):#일부날짜안됨
    name = "NESCO_international"
    allowed_domains = ["www.nesco.gov.bd"]
    start_urls = ['http://nesco.gov.bd/site/view/tenders_type/%E0%A6%86%E0%A6%A8%E0%A7%8D%E0%A6%A4%E0%A6%B0%E0%A7%8D%E0%A6%9C%E0%A6%BE%E0%A6%A4%E0%A6%BF%E0%A6%95/-']
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '8000000',
        'DOWNLOAD_TIMEOUT' : '90',
        'DOWNLOAD_MAXSIZE' : '11000000',#10mb..
        'RETRY_ENABLED' : 'False',   
    }    

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.browser = webdriver.Chrome(path_webdriver)

    def parse(self, response):
        self.browser.get(response.url)
        time.sleep(5)  

        html = self.browser.find_element_by_xpath('//*').get_attribute('outerHTML')
        selector = Selector(text=html)

        rows = selector.xpath('//*[@id="example"]/tbody/tr')
        for row in rows:
            item = NewscrawlingItem()
            hrefs = []
            for href in row.xpath('./td[6]/div/a'):
                hrefs.append(href.xpath('.//@href')[0].extract())
            documents = []
            file_urls = []
            description = row.xpath('./td[2]/text()')[0].extract()
            issuanceTime = row.xpath('./td[4]/text()').get()
            openTime = row.xpath('./td[5]/text()').get()
            for url in hrefs:
                url = response.urljoin(url)
                file_urls.append(url)
                url = exchanger(url)
                documents.append(url)
            item['Company'] = "NESCO_international"
            item['Documents'] = ','.join(documents)
            item["Bid_Descriptions"] = ""
            try:
                item['Bid_IssuanceTime'] = str(parse(issuanceTime))
            except:
                item['Bid_IssuanceTime'] = ""
            try:
                item['Bid_OpenTime'] = str(parse(openTime))
            except:
                item['Bid_OpenTime'] = "" 
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = len(documents)
            item['Qty_DownDoc'] = 0

            fetchall = dbCheck(item)
            if  fetchall:
                pass
            else:
                yield item
                for file_url in file_urls:
                    yield scrapy.Request(
                        url= file_url,
                        callback=save_pdf,
                        dont_filter=True,
                    )  



process = CrawlerProcess(get_project_settings())

process.crawl(ASPOWER)
process.crawl(ESCOM)
process.crawl(UMEME)
process.crawl(GUAM)
process.crawl(HESCO)
process.crawl(KENYA)
process.crawl(MOEE)
process.crawl(NPC)

###################

process.crawl(APSCL)
process.crawl(DPDC)
process.crawl(BREB)
process.crawl(PBS)
process.crawl(WZPDCL_local)
process.crawl(WZPDCL_international)
process.crawl(NESCO_LOCAL)
process.crawl(NESCO_international)

process.start() # the script will block here until all crawling jobs are finished