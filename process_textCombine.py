import glob
import os
from os.path import basename

def process_textCombine():
    target_dir = "C:/Users/wlsdk/newscrawling/Files/*"
    path_names = glob.glob(target_dir, recursive=True)
    for path_name in path_names:
        target_dir = path_name + "/*.txt"
        path_names = glob.glob(target_dir, recursive=True)
        with open(path_name + "/result.txt", "wb") as outfile:
            for path_name in path_names:
                with open(path_name, "rb") as infile:
                    outfile.write(infile.read())
                    infile.close()

                re_path_name = '.'.join(path_name.split('.')[:-1])
                if not 'result' in re_path_name:                    
                    os.remove(re_path_name + '.txt')
                    os.remove(re_path_name + '.jpg')
                    print("remove " + re_path_name + '.txt')
                    print("remove " + re_path_name + '.jpg')
            outfile.close()        
            print("create resuelt.txt")      