import glob
import os
import sqlite3
from os.path import basename

def process_kwSearch():
    cats_analogue={"TRANSFORMER":["converter","transformer"],
         "SWITCH GEARS":["switch"],
         "OLBS":["olbs","oil Immersed Loadbreak Switch","Switch","Loadbreak","Load break","breaker"],
         "CABLE":["cable", "conductors", "insulating", "wire", "cables"],
         "INSULATOR":["insulator", "electrical insulator","Ceramic insulator"],
         "ARRESTOR":["arrester","Surge","lightning","surge diverter", "diverter", "protect", "protector", "Lightning rod"],
         "FUSES":["fuse", "fusing", "fuse-base", "fuse-link", "drop-out", "fuse-carrier", "fuse-element", "melt", "cos", "cut", "cutout", "holder"],
         "OCR":["ocr", "protective", "relay", "power", "Power","current", "overcurrent", "digital", "protection", "microprocessor"],
         "UPS":["ups", "load"],
         "CONSTRUCTION":["construction"],
         "Boundary wall":["wall"],
         "CIRCUIT":["circuit"],
         "FILLIMG":["filling"],
         "FLOORING":["flooring"],
         "BUILDING":["building"],
         "STATION":["station"],
         "TIRE":["tire","tires","tire","tires"],
         "TUBE":["tube"],
         "SERVICE":["service"],
         "PLANT":["plant"],
         "RECORD":["record"],
         "SCANNING":["scanning"],
         "METER":["meter"],
         "EQUIPMENT":["equipment"],
         "BRACKET":["bracket"],
         "DISPLAY":["display", "moniter"],
         "DISTRIBUTION LINE":["distribution line"],
         "RECLOSER":["recloser"],
         "PARTS":["parts"],
         "SHOCKS":["shock"],
         "DETAILING":["detailing"],
         "ENGINE":["engine"],
         "TANK":["tank"],
         "CAMERA":["camera"],
         "TONER CARTRIDGE":["toner","cartridge"],
         "TELEPHONE":["telephone"],
         "OUTLET":["outlet","extention"],
         "STEEL":["steel"],
         "POLE":["pole"],
         "GAUGE":["gauge"],
         "PAD":["pad"],
         "STICKER":["sticker"],
         "PEN":["pen"],
         "PAPER":["paper"],
         "STAMP":["stamp"],
         "BRUSH":["brush"],
         "APPLIANCES":["appliances"],
         "AIRCONDITION":["aircondition"],
         "HIGHLIGHTER":["highlighter"],
         "GENERATOR":["generator"," generating","dynamo"],
         "BATTERIES":["Batteries", "battery", "Charger", "Chargers"]
         }    

    updateSql = """update tender set Category = '{0}' where id = '{1}'"""
    conn = sqlite3.connect("C:/Users/wlsdk/newscrawling/tender.db")
    cur = conn.cursor()

    target_dir = "C:/Users/wlsdk/newscrawling/Files/*/*.txt"
    path_names = glob.glob(target_dir, recursive=True)

    for path_name in path_names:
        catList = []
        print(path_name)
        print(path_name.split('\\')[-2])
        with open(path_name, 'r', encoding='UTF8') as f:
            text = f.read()
            for key, values in cats_analogue.items():
                for value in values:
                    if value in text:
                        catList.append(key)          

        my_set = set(catList)
        catList = list(my_set) 
        print(basename(path_name).split('.')[0])
        cur.execute(updateSql.format(','.join(catList), path_name.split('\\')[-2]))
        conn.commit()
