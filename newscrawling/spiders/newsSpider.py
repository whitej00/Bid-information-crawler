import scrapy
import time
import datetime
import sqlite3
import os
from newscrawling.items import NewscrawlingItem
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet.error import TimeoutError, TCPTimedOutError

path_webdriver = "C:/Aspace/Utility/Chrome Dirver/chromedriver.exe"

def save_pdf(response):
    path = response.url.split('/')[-1]
    url = response.url
    url = url.replace("'","[apos]")
    url = url.replace('"','[quot]')

    conn = sqlite3.connect("tender.db")
    cur = conn.cursor()
    
    idSql = """SELECT id FROM 'tender' where documents like '%{0}%'""".format(path)
    countSql = """update tender set Qty_DownDoc = Qty_DownDoc + 1 where Documents like '%{0}%'""".format(url)
    checkSql = """select Qty_TotalDoc, Qty_DownDoc from tender where Documents like '%{0}%'""".format(url)
    updateSql = """update tender set Down_Status = '{0}' where Documents like '%{1}%'"""

    cur.execute(idSql)
    dbId = cur.fetchall()
    dbId = str(dbId[0][0])

    if not os.path.isdir("C:/Users/wlsdk/newscrawling/Files/{0}".format(dbId)):
        os.mkdir("C:/Users/wlsdk/newscrawling/Files/{0}".format(dbId))
        
    with open('Files/' + dbId + '/' + path, 'wb') as f:
        f.write(response.body)
  
    cur.execute(countSql)
    conn.commit()
    cur.execute(checkSql)
     
    fetch = cur.fetchall()
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print(fetch)
    
    if fetch[0][0] == fetch[0][1]:
        cur.execute(updateSql.format('o', response.url))
        conn.commit()
    else:
        cur.execute(updateSql.format('x', response.url))
        conn.commit()  

def dbCheck(doc):
    conn = sqlite3.connect("tender.db")
    cur = conn.cursor()
    selectSql = """select * from tender where Documents like '%{0}%'""".format(doc)
    cur.execute(selectSql)

    return cur.fetchall()

class ASPOWER(scrapy.Spider):
    name = "ASPOWER"
    allowed_domains = ["www.aspower.com"]
    start_urls = ["https://www.aspower.com/aspa-procurement-01.html"]
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '1073741824',
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
            documents = ",".join(urls)           
            documents = documents.replace("'","[apos]") 
            documents = documents.replace('"','[quot]')
      
            issuanceTime= row.xpath('./td[2]/span/text()')[0].extract()
            dueDate = row.xpath('./td[2]/span/text()')[1].extract()

            item['Company'] = "ASPOWER"
            item['Documents'] = documents
            item['Bid_IssuanceTime'] = issuanceTime
            item['Bid_OpenTime'] = dueDate
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = len(urls)
            item['Qty_DownDoc'] = 0
                  
            fetchall = dbCheck(item['Documents'])
            if  fetchall:
                self.count += 1
                if self.count == 3:
                    break
                pass
            else:
                yield item

                for url in urls:
                    yield scrapy.Request(
                        url=response.urljoin(url),
                        callback=save_pdf,
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
        'DOWNLOAD_WARNSIZE': '1073741824',
        'RETRY_ENABLED' : 'False',
    }
    fileDown = 0
    count = 0

    def __init__(self):
        scrapy.Spider.__init__(self)

    def parse(self, response):

        rows = response.xpath('//*[@id="table1"]/tbody/tr')
        item = NewscrawlingItem()

        for row in rows:
            documents = response.urljoin(row.xpath('td[2]/a/@href')[0].extract()).replace(" ","%20")

            item['Company'] = "ESCOM"
            item['Documents'] = documents
            item['Bid_IssuanceTime'] = ''
            item['Bid_OpenTime'] = ''
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = 1
            item['Qty_DownDoc'] = 0
   
            fetchall = dbCheck(item['Documents'])
            if  fetchall:
                self.count += 1
                if self.count == 3:
                    break
                pass
            else:
                yield item
                yield scrapy.Request(
                    url= documents,
                    callback=save_pdf,
                    errback=self.errback,
                )     
    def errback(self, failure):
        if failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

class UMEME(scrapy.Spider):
    name = "UMEME"
    allowed_domains = ["www.umeme.co.ug"]
    start_urls = ["https://www.umeme.co.ug/tenders"]
    custom_settings = {
        'DOWNLOAD_WARNSIZE': '1073741824',
        'RETRY_ENABLED' : 'False',
    }
    fileDown = 0
    count = 0

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.browser = webdriver.Chrome(path_webdriver)

    def parse(self, response):
        self.browser.get(response.url)
        time.sleep(5)  

        html = self.browser.find_element_by_xpath('//*').get_attribute('outerHTML')
        selector = Selector(text=html)

        rows = selector.xpath('//*[@id="root"]/div[1]/div[1]/div[2]/div[7]/table/tbody/tr')
        length = len(rows)

        item = NewscrawlingItem()

        for row in rows:
            documents = row.xpath('td[4]/a/@href')[0].extract()

            item['Company'] = "UMEME"
            item['Documents'] = documents
            item['Bid_IssuanceTime'] = ''
            item['Bid_OpenTime'] = ''
            item['InputTime'] = datetime.datetime.now()
            item['Down_Status'] = 'x'
            item['Qty_TotalDoc'] = 1
            item['Qty_DownDoc'] = 0

               
            fetchall = dbCheck(item['Documents'])
            if  fetchall:
                self.count += 1
                if self.count == 3:
                    break
                pass
            else:
                yield item
                yield scrapy.Request(
                    url= documents,
                    callback=save_pdf,
                )   

process = CrawlerProcess(get_project_settings())
process.crawl(ASPOWER)
process.crawl(ESCOM)
process.crawl(UMEME)
process.start() # the script will block here until all crawling jobs are finished
