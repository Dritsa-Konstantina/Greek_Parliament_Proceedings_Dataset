# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import csv
import datetime
from selenium import webdriver
import time

now = datetime.datetime.now()

with open('../out_files/original_members_data.csv','w+',
          encoding='utf-8') as original_members_data:

    csv_writer = csv.writer(original_members_data, delimiter=',')

    _URL = 'http://www.hellenicparliament.gr/Vouleftes/Diatelesantes' \
           '-Vouleftes-Apo-Ti-Metapolitefsi-Os-Simera/'

    # chromedriver.exe located in the same folder as the script
    driver = webdriver.Chrome('./chromedriver')
    time.sleep(5)
    driver.get(_URL)
    time.sleep(5) #page load time
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    time.sleep(2)

    #Get dropdown list
    members_dropdown = soup.find("select", id="ctl00_ContentPlaceHolder1_dmps_mpsListId")

    members_links={}

    #Store all links and members' names in a dictionary
    for option in members_dropdown.find_all('option'):
        members_links[option['value']] = option.get_text()

    print('Total list length: ', (len(members_links)-1))

    member_counter=0

    for link, member in members_links.items():

        if member!='' and member!=' Επιλέξτε Βουλευτή':

            member_counter+=1
            if member_counter%50==0:
                time.sleep(15)
            print(str(member_counter)+' from '+str(len(members_links)-1))
            print("Name: ",member)
            member_URL = _URL+'?MpId='+link
            print("Processing page ",member_URL,"\n")

            driver.get(member_URL)
            time.sleep(3)
            html = driver.page_source
            soup_member = BeautifulSoup(html, "html.parser")

            #if the page has no table
            if not soup_member.find("tbody"):
                original_members_data.write('No:'+str(member_counter)+',Name:'+member+',NO DATA\n')

            else:
                trs = soup_member.find("tbody").find_all("tr", {"class":["odd", "even"]})

                for tr in trs:

                    td_columns = [td.getText() for td in tr.find_all("td")]

                    period = td_columns[0]
                    period = re.sub(r"\s+", "", period)
                    if '-)' in period:

                        # for example Period:ΙΖ΄(20/09/2015-) means it continues up to today
                        period = re.sub('-\)', '-'+ now.strftime("%d/%m/%Y")+')', period)

                    date = td_columns[1]
                    date = re.sub(r"\s+", "", date)

                    administrative_region = td_columns[2]
                    administrative_region = re.sub(r"\s+", "", administrative_region)

                    parliamentary_party = td_columns[3]
                    parliamentary_party = re.sub(r"\s+", "", parliamentary_party)

                    description = td_columns[4]
                    description = re.sub(r"\s+", "", description)

                    csv_writer.writerow(['No:'+str(member_counter),
                                         'Name:'+member,
                                         'Period:'+period,
                                         'Date:'+date,
                                         'Administrative-Region:'+administrative_region,
                                         'Parliamentary-Party:'+parliamentary_party,
                                         'Description:'+description])

    driver.close()