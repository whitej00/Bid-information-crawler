import process_pdf2image, process_tesseract, process_textCombine, process_kwSearch, process_pdf2text
import time
import os
import sqlite3

def run_process():
    # start crawling
    os.system('scrapy crawl')

    date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    distingSql = """SELECT id FROM 'tender' WHERE InputTime like '%{0}%'"""
    
    conn = sqlite3.connect("/srv1/process/tender.db")
    cur = conn.cursor()
    cur.execute(distingSql.format(date))
    fetchall = cur.fetchall()

    # start process_pdf2text
    process_pdf2text.process_pdf2text(fetchall)
    time.sleep(3)
    # start process_textCombine
    process_textCombine.process_textCombine(fetchall)
    time.sleep(3)
    # start process_kwSearch
    process_kwSearch.process_kwSearch(fetchall)
run_process()    