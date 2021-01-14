import process_pdf2image, process_tesseract, process_textCombine, process_kwSearch, process_pdf2text
import time
import os
import sqlite3

def run_process():
    # start crawling
    os.system('scrapy crawl')

    date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    distingSql = """SELECT id FROM 'tender' WHERE InputTime like '%{0}%' and ScanDisting like '%{1}%' """
    
    conn = sqlite3.connect("/srv1/process/tender.db")
    cur = conn.cursor()
    cur.execute(distingSql.format(date, 'x'))# text pdf
    fetchall = cur.fetchall()

    # start process_pdf2text
    process_pdf2text.process_pdf2text(fetchall)
    time.sleep(3)
    # start process_kwSearch
    process_kwSearch.process_kwSearch(fetchall)

    cur.execute(distingSql.format(date, 'o'))# scan pdf
    fetchall = cur.fetchall()
    if fetchall:
        # start process_pdf2image
        process_pdf2image.process_pdf2image(fetchall)
        time.sleep(3)
        # start process_tesseract
        process_tesseract.file_list(fetchall)
        time.sleep(3)
        # start process_textCombine
        process_textCombine.process_textCombine(fetchall)
        time.sleep(3)
        # start process_kwSearch
        process_kwSearch.process_kwSearch(fetchall)
run_process()    