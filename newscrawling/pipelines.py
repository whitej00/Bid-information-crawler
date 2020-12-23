import sqlite3

class CsvPipeline(object):
    def __init__(self):
        self.conn = sqlite3.connect("tender.db")
        self.cur = self.conn.cursor()
        self.cur.execute("""create table if not exists tender (
                                            id integer primary key autoincrement,
                                            Company TEXT,
                                            Documents TEXT,
                                            Bid_Descriptions TEXT,
                                            Bid_IssuanceTime TEXT,
                                            Bid_OpenTime TEXT,
                                            InputTime TEXT,
                                            Category TEXT,
                                            Down_Status TEXT,
                                            Qty_TotalDoc INTEGER,
                                            Qty_DownDoc INTEGER,
                                            Qty_Image INTEGER,
                                            Qty_Hocr INTEGER,
                                            Text INTEGER
                                            )""")
        self.count = 0                                    

    def process_item(self, item, spider):
        insertSql = """
                    insert into 
                    tender (Company, Documents, Bid_IssuanceTime, Bid_OpenTime, InputTime, Down_Status, Qty_TotalDoc, Qty_DownDoc) 
                    values ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", {6}, {7})
                    """.format(
                        item['Company'],
                        item['Documents'],
                        item['Bid_IssuanceTime'],
                        item['Bid_OpenTime'],
                        item['InputTime'],
                        item['Down_Status'],
                        item['Qty_TotalDoc'],
                        item['Qty_DownDoc'],
                        )

        selectSql = """select * from tender where Documents like '%{0}%'""".format(item['Documents'])

        self.cur.execute(selectSql)
        if  self.cur.fetchall():
            raise CloseSpider('force exit!!')
        else:
            self.cur.execute(insertSql)
            self.conn.commit()

        return item  
        