import subprocess
import pandas as pd
import time
import os

# -*- Get all the zones -*-
try:
    os.remove('./additional_csv/zones.csv')
except Exception as e:
    print(e)

command_zone = 'scrapy crawl getZones -o ./additional_csv/zones.csv'
subprocess.run(command_zone, shell=True)

# -*- Load zone dataframe -*-
all_zones = pd.read_csv('./additional_csv/zones.csv')

# -*- Get all the links -*-
for zone in all_zones.iloc[:].itertuples():
    print("\n***********************")
    print(f"Extracting {zone.type} houses links from {zone.zone}")
    print("***********************\n\n")
    time.sleep(3)

    command_links = f'scrapy crawl getLinks -a start={zone.zone} -o ./additional_csv/links.csv'
    subprocess.run(command_links, shell=True)
    print("********   PROVINCE LINK EXTRACTION FINISHED!   Waiting 45 seconds before starting with new province")
    time.sleep(45)

# -*- Get all the denied links -*-
denied_flag = True
while denied_flag:
    denied_links = []
    try:
        with open('logLink.txt') as log:
            denied_links = log.readlines()
            denied_links = [s.strip() for s in denied_links]
        try:
            os.remove('logLink.txt')
        except:
            denied_flag = False

        print("\n***********************")
        print(f"Extracting denied {len(denied_links)} houses links")
        print("***********************\n\n")
        time.sleep(3)

        for link in denied_links:
            command_denied = f'scrapy crawl getLinks -a start={link} -o ./additional_csv/links.csv'
            subprocess.run(command_denied, shell=True)

        # -*- Check if still are denied links -*-
        if os.path.isfile('./logLink.txt'):
            print("********   STILL ARE DENIED LINKS! Waiting 3 minutes before restarting extraction")
            time.sleep(180)
        else:
            denied_flag = False
    except:
        denied_flag = False