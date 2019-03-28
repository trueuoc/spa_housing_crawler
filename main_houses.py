import subprocess
import pandas as pd
import time
import tkinter as tk
import os

# -*- Load links dataframe -*-
exclude = [i for i, line in enumerate(open('links.csv')) if line.startswith('link')]
if len(exclude) is 1:
    all_zones = pd.read_csv('links.csv')
else:
    all_zones = pd.read_csv('links.csv', skiprows=exclude[1:])

provinces = all_zones.province.unique()

# -*- Select provinces with GUI
selected=[]
def selection():
    sel_provinces=l.curselection() # current selection
    for province in sel_provinces:
        selected.extend([l.get(province)])
    root.destroy()

root = tk.Tk()
l = tk.Listbox(root, width=50, height=25, selectmode=tk.MULTIPLE)
b = tk.Button(root,text="Select province(s)",command=selection)

for index in range(len(provinces)):
    l.insert(index, provinces[index])
l.pack()
b.pack()
root.geometry("500x500+500+100")
root.mainloop()

# -*- Extract houses from selected provinces
for province in selected:
    filtered_zones = all_zones[all_zones['province'] == province]
    num_link = sum(all_zones[all_zones['province'] == province]['num_link'])

    print("\n***********************")
    print(f"Crawler is ready to extract {num_link} houses from {province}")
    print("***********************\n")
    time.sleep(3)

    for zone in filtered_zones.itertuples():
        print("\n***********************")
        print(f"Extracting {zone.num_link} houses from a zone of {province}")
        print("***********************\n\n")
        time.sleep(3)

        command = f'scrapy crawl houses -a start_url={zone.link} -o houses_{province.replace(" ", "_")}.csv'
        subprocess.run(command, shell=True)
        print("********   ZONE HOUSE EXTRACTION FINISHED!   Waiting 20 seconds before reload")
        time.sleep(20)

# -*- Get denied links of selected province -*-
deny_link_flag = True
while deny_link_flag:
    denied_links = []
    try:
        with open('logLink.txt') as log:
            denied_links.extend(log.readlines())
            denied_links = [s.strip() for s in denied_links]
        try:
            os.remove('logLink.txt')
        except Exception as e:
            print(e)
            deny_link_flag = False
        print("\n***********************")
        print(f"Extracting denied houses links from {province}")
        print("***********************\n\n")
        print("********   Waiting 3 minutes before starting")
        time.sleep(180)

        for link in denied_links:
            command_denied_link = f'scrapy crawl houses -a start_url={link} -o houses_{province.replace(" ","_")}.csv'
            subprocess.run(command_denied_link, shell=True)

        # -*- Check if still are denied houses -*-
        if os.path.isfile('logLink.txt'):
            print("********   STILL ARE DENIED LINKS! Waiting 2 extra minutes before reload")
            time.sleep(120)
        else:
            deny_link_flag = False
    except Exception as e:
        deny_link_flag = False

# -*- Get denied houses of selected province -*-
if os.path.isfile('logHouse.txt'):
    deny_house_flag = True
else:
    deny_house_flag = False

while deny_house_flag:
    print("\n***********************")
    print(f"Extracting denied houses links from {province}")
    print("***********************\n\n")
    print("********   Waiting 3 minutes before starting")
    time.sleep(180)
    denied_link = 'https://www.idealista.com/login'  # start-url-code to extract denied links
    command_denied_house = f'scrapy crawl houses -a start_url={denied_link} -o houses_{province.replace(" ","_")}.csv'
    subprocess.run(command_denied_house, shell=True)

    # -*- Check if still are denied houses -*-
    if os.path.isfile('./logHouse.txt'):
        print("********   STILL ARE DENIED HOUSES! Waiting 2 extra minutes before reload")
        time.sleep(120)
    else:
        deny_house_flag = False