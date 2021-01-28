import glob
import os
import sqlite3
from os.path import basename

def process_kwSearch(fetchall):
    cats_analogue = {
        "TRANSFORMER":["converter","transformer"],
        "SWITCH":["switch"],
        "OLBS":["olbs","oil Immersed Loadbreak Switch","Switch","Loadbreak","Load break","breaker"],
        "CABLE":["cable", "conductors", "insulating", "wire", "cables"],
        "INSULATOR":["insulator", "electrical insulator","Ceramic insulator"],
        "ARRESTOR":["arrester","Surge","lightning","surge diverter", "diverter", "protect", "protector", "Lightning rod"],
        "FUSES":["fuse", "fusing", "fuse-base", "fuse-link", "drop-out", "fuse-carrier", "fuse-element", "melt", "cos", "cut", "cutout", "holder"],
        "UPS":["ups", "Uninterruptible Power Supply","Power Supply"],
        "METER":["meter","watt-hour meter","ectricity meter"],
        "GENERATOR":["generator"," generating","dynamo"],
        "BATTERIES":["Batteries", "battery", "Charger", "Chargers"],
        "MOTOR":["motor"],
        "BREAKER":["circuit breaker"],
        "DISTRIBUTING BOARD":["distributing board","plane", "switchboard", "panel board"],
         }

    updateSql = """update tender set Category = '{0}' where id = '{1}'"""
    conn = sqlite3.connect("/srv1/process/tender.db")
    cur = conn.cursor()

    path_names = []
    globs = []
    target_dir = "/srv1/process/Files/{0}/*.txt"
    for fetch in fetchall:
        globs = glob.glob(target_dir.format(fetch[0]), recursive=True)
        for a in globs:
            path_names.append(a)

    for path_name in path_names:
        catList = []
        print(path_name)
        with open(path_name, 'r', encoding='UTF8') as f:
            text = f.read()
            for key, values in cats_analogue.items():
                for value in values:
                    if value in text:
                        catList.append(key)          

        my_set = set(catList)
        catList = list(my_set) 
        cur.execute(updateSql.format(','.join(catList), path_name.split('\\')[-2].split('/')[-1]))
        conn.commit()    