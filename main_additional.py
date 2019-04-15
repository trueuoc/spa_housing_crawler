import subprocess
import os


try:
    os.remove('./additional_csv/addinfo.csv')
except Exception as e:
    print(e)

command_zone = 'scrapy crawl getAditionalData -o ./additional_csv/addinfo.csv'
subprocess.run(command_zone, shell=True)