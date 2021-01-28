import process_pdf2image, process_tesseract
import time

def run_process(fetch):
    # start process_pdf2image
    process_pdf2image.process_pdf2image(fetch)
    time.sleep(3)
    # start process_tesseract
    process_tesseract.file_list(fetch)