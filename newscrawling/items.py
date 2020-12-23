import scrapy
 
class NewscrawlingItem(scrapy.Item):
    Company = scrapy.Field()
    Documents = scrapy.Field()
    Bid_Descriptions = scrapy.Field()
    Bid_IssuanceTime = scrapy.Field()
    Bid_OpenTime = scrapy.Field()
    InputTime = scrapy.Field()
    Down_Status = scrapy.Field()
    Qty_TotalDoc = scrapy.Field()
    Qty_DownDoc = scrapy.Field()
    Qty_Image = scrapy.Field()
    Qty_Hocr = scrapy.Field()
    Text = scrapy.Field()
    pass

