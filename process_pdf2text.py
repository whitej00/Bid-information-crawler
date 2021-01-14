import PyPDF2
import glob
import os
from os.path import basename, dirname

def process_pdf2text(fetchall):
    path_names = []
    globs = []
    target_dir = "/srv1/process/Files/{0}/*.pdf"
    for fetch in fetchall:
        globs = glob.glob(target_dir.format(fetch[0]), recursive=True)
        for a in globs:
            path_names.append(a)

    for path_name in path_names:
        print(path_name)
        with open(dirname(path_name) + '/result.txt', 'ab') as f:
            file = open(path_name, 'rb')
            fileReader = PyPDF2.PdfFileReader(file)
            fileReader.documentInfo
            numPages = fileReader.numPages

            for numPage in range(numPages):
                print(str(numPage+1) + '/' + str(numPages))
                pageObj = fileReader.getPage(numPage)
                text = pageObj.extractText()
                f.write(text.encode())
