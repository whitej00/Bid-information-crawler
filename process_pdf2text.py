import PyPDF2
import glob
import processScan
from os.path import basename, dirname

def process_pdf2text(fetchall):
    path_names = []
    globs = []
    target_dir = "/srv/ucproject/bid/static/bid/Files/{0}/*.pdf"
    for fetch in fetchall:
        globs = glob.glob(target_dir.format(fetch[0]), recursive=True)
        idenL = 0
        for path_name in globs:
            print(path_name)
            iden = ""
            with open(dirname(path_name) + '/result.txt', 'ab') as f:
                file = open(path_name, 'rb')
                fileReader = PyPDF2.PdfFileReader(file, strict=False)
                fileReader.documentInfo
                numPages = fileReader.numPages

                for numPage in range(numPages):
                    print(str(numPage+1) + '/' + str(numPages))
                    pageObj = fileReader.getPage(numPage)
                    text = pageObj.extractText()
                    iden += text
                    f.write(text.encode())     

            if not iden:
                idenL += 1
        if idenL > 0:
            processScan.run_process(fetch[0])
