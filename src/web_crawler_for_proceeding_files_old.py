# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import time
import requests
import codecs

""" This script is currently not working properly since the Greek Parliament website
    installed cyber security software in 2020. However, a big part of the data for 
    this dataset was collected with this script, before the installation of the new software. 
    The script that succeeded this one is named web_crawler_for_proceeding_files.py """

def record_retrieval(files, downloaded_counter, href, tr, ext):

    downloaded_counter+=1
    print("No. ",downloaded_counter)
    file_URL = domain+href
    print("File url: ",file_URL)

    td_columns = [td.getText().lower() for td in tr.find_all("td")[:4]] #get text from 4 first columns
    date = td_columns[0]
    period = td_columns[1]
    session = td_columns[2]
    sitting = td_columns[3]

    # For the selected table row return the value of the first column (date column)
    date = (date.replace("/", "-")).replace(" ", "")
    reversed_date = date[6:10]+date[5]+date[3:5]+date[2]+date[0:2]

    if len(files)==0:
        get_html(file_URL, downloaded_counter,reversed_date, period, session, sitting, ext)

    else:
        get_file(file_URL, downloaded_counter,reversed_date, period, session, sitting, ext)

    #Add sleeping time for the script every 1000 files
    if ((downloaded_counter!=0) and ((downloaded_counter % 1000) == 0)):
        print("Let's sleep for 5 minutes...")
        time.sleep(300)
        print("Up and running again...")

    return downloaded_counter


def get_html(file_URL, downloaded_counter,reversed_date, period, session, sitting, ext):

    nested_response = requests.get(file_URL)
    inner_html = nested_response.text
    soup2 = BeautifulSoup(inner_html, "html.parser")
    plain_content = soup2.find("span", id="ctl00_ContentPlaceHolder1_sri_lblBody").get_text(separator="\n")

    # segments separated with underscore
    path = '../original_data/'+reversed_date+"_"+str(downloaded_counter)+"_"+period+"_"+session+"_"+sitting+"."+ext
    with codecs.open(path,'w+', encoding='utf-8') as new_file:
        new_file.write(plain_content)

    print("Saved as "+path,"\n")


def get_file(file_URL, downloaded_counter,reversed_date, period, session, sitting, ext):

    path = '../original_data/'+reversed_date+'_'+ str(downloaded_counter)+"_"+period+"_"+session+"_"+sitting+"."+ext

    filecontent = requests.get(file_URL)
    with open(path,'wb') as f: #open file in binary mode
        f.write(filecontent.content)
        f.close()

    print("Saved as "+path,"\n")

domain = "http://www.hellenicparliament.gr"
_URL = 'http://www.hellenicparliament.gr/Praktika/Synedriaseis-Olomeleias?pageNo='
url_part = "/UserFiles/"
downloaded_counter=0

#Open a file in order to write down the rows with no files
no_files = codecs.open('../out_files/rows_with_no_files.txt','w+', encoding='utf-8')

for pageNo in range(17, 0, -1):
    page_URL = _URL+str(pageNo)
    print("Processing page", pageNo, "\n")

    response = requests.get(page_URL)
    html = response.text #.content -> response as bytes, .text-> response as unicode/string
    soup = BeautifulSoup(html, "html.parser")

    # From the table body (tbody) take all table rows (trs) that should
    # contain record files, excluding footer row
    trs = soup.find("tbody").find_all("tr", {"class":["odd", "even"]})

    for tr in trs:

        files={} #dictionary with file extensions as keys and their links as values

        # From each table row return all the links
        for link in tr.findAll('a', href=True):

            href = link.get('href')

            # Keep the links that lead to the requested files and the
            # corresponding filetypes
            if url_part in href:
                files.update({href.split(".")[-1]: href})

        #If the row has no record files
        if len(files)==0:
            # write the page number & row date in the file rows_with_no_files.txt
            no_files.write('Page '+str(pageNo)+" and date "+tr.find('td').getText()+" \n")
            print("No file found. Opening ", href)
            downloaded_counter = record_retrieval(files, downloaded_counter, href, tr, 'txt')

        else:
            # Download the file with the following preference order
            if "txt" in (ext.lower() for ext in files.keys()):
                downloaded_counter = record_retrieval(files, downloaded_counter, href, tr, "txt")
            elif "docx" in (ext.lower() for ext in files.keys()):
                downloaded_counter = record_retrieval(files, downloaded_counter, href, tr, "docx")
            elif "doc" in (ext.lower() for ext in files.keys()):
                downloaded_counter = record_retrieval(files, downloaded_counter, href, tr, "doc")
            elif "pdf" in (ext.lower() for ext in files.keys()):
                downloaded_counter = record_retrieval(files, downloaded_counter, href, tr, "pdf")

no_files.close()