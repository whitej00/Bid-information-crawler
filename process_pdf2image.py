import glob
import os
from pdf2image import convert_from_path, pdfinfo_from_path
from os.path import basename

def process_pdf2image(fetch):
    path_names = []
    globs = []
    target_dir = "/srv/ucproject/bid/static/bid/Files/{0}/*.pdf"
    globs = glob.glob(target_dir.format(fetch), recursive=True)
    for path_name in globs:
        dir_name = os.path.dirname(path_name)
        info = pdfinfo_from_path(path_name, userpw = None)
        maxPages = info["Pages"]
        successPage = 0
        print(path_name)

        for pageNum in range(1, maxPages+1, 10):
            pages = convert_from_path(path_name, dpi=100, first_page=pageNum, last_page = min(pageNum+10-1,maxPages))

            for page in pages:
                formatPNum = format(pageNum,'03')
                page.save(dir_name + '/{0}{1}.jpg'.format('.'.join(basename(path_name).split('.')[:-1]),formatPNum), 'JPEG')
                pageNum += 1
                successPage += 1
                print(str(successPage) + "/" + str(maxPages))
