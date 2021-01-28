import glob
import os
from os.path import basename, dirname

def process_textCombine(fetchall):
    target_dir = "/srv1/process/Files/{0}"
    for fetch in fetchall:  
        if os.path.isdir(target_dir.format(str(fetch[0]))) == True:
            path_names = glob.glob(target_dir.format(str(fetch[0]) + "/*.txt"), recursive=True)
            with open(target_dir.format(fetch[0]) + "/finalresult.txt", "wb") as outfile:
                for path_name in path_names: 
                    print(path_name)
                    with open(path_name, "rb") as infile:
                        outfile.write(infile.read())
                        infile.close()  

                outfile.close()        
                print("create finalresult.txt")    

            txtrmL = glob.glob(target_dir.format(str(fetch[0]) + "/*.txt", recursive=True))
            for txt in txtrmL:
                if 'finalresult' in txt:
                    pass            
                else:
                    os.remove(txt)
                    print("remove : " + txt)


            jpgrmL = glob.glob(target_dir.format(str(fetch[0]) + "/*.jpg", recursive=True))
            for jpg in jpgrmL:
                os.remove(jpg)
                print("remove : " + jpg)