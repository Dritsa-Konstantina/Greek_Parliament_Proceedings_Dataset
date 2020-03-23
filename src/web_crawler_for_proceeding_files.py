# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import time
import os
import shutil
import codecs
from selenium import webdriver
import ntpath
import urllib.parse


def create_target_path(target_data_folder, tr, entry_counter, ext):

    td_columns = [td.getText().lower() for td in tr.find_all("td")[:4]] #get text from 4 first columns
    date = td_columns[0]
    period = td_columns[1]
    session = td_columns[2]
    sitting = td_columns[3]

    # For the selected table row return the value of the first column (date column)
    date = (date.replace("/", "-")).replace(" ", "")
    reversed_date = date[6:10]+date[5]+date[3:5]+date[2]+date[0:2]

    target_filename = reversed_date+'_'+ str(entry_counter)+"_"+period+"_"+session+"_"+sitting+"."+ext
    target_path = os.path.join(target_data_folder, target_filename)

    return(target_path)

def download_file(driver, downloaded_data_folder, file_URL, target_path):

    element = driver.find_element_by_xpath('//a[@href="' + file_URL + '"]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    element.click()

    # wait for full download
    time.sleep(7)

    downloaded_file_path = os.path.join(downloaded_data_folder, ntpath.basename(file_URL))

    #unquote: decode url to match downloaded filename (often in cases with Greek letters in filename)
    shutil.copy(urllib.parse.unquote(downloaded_file_path), target_path)  # copy and rename file


domain = "https://www.hellenicparliament.gr"
_URL = 'https://www.hellenicparliament.gr/Praktika/Synedriaseis-Olomeleias?pageNo='
url_part = "/UserFiles/"
entry_counter = 0
downloaded_data_folder = '../original_data_download_folder/'
target_data_folder = '../original_data/'

#set preferred download folder
chromeOptions = webdriver.ChromeOptions()
prefs = {"profile.default_content_settings.popups": 0,
         "download.default_directory" : os.path.abspath(downloaded_data_folder),
         "directory_upgrade": True}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chromeOptions)


#Open a file in order to write down the rows with no files
no_files = codecs.open('../out_files/rows_with_no_files.txt','w+', encoding='utf-8')

# Choose range of pages
for pageNo in range (100,0,-1):
    print('Sleeping 5 seconds')
    page_URL = _URL+str(pageNo)
    print("Processing page",pageNo,"\n")
    driver.get(page_URL)
    time.sleep(5)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    trs = soup.find("tbody").find_all("tr", {"class":["odd", "even"]})

    for tr in trs:

        entry_counter += 1
        print("No. ", entry_counter)

        files={} #dictionary with file extensions as keys and their links as values

        # From each table row return all the links
        for link in tr.findAll('a', href=True):

            href = link.get('href')

            # Keep the links that lead to the requested files and the
            # corresponding filetypes
            if url_part in href:
                files.update({(href.split(".")[-1]).lower(): href})

        if len(files)==0:
            no_files.write('Page ' + str(pageNo) + " and date " + tr.find(
                'td').getText() + " \n")
            print('File not found')
        else:
            # Download the file with the following preference order
            if "txt" in (ext.lower() for ext in files.keys()):
                file_ext = 'txt'
            elif "docx" in (ext.lower() for ext in files.keys()):
                file_ext = 'docx'
            elif "doc" in (ext.lower() for ext in files.keys()):
                file_ext = 'doc'
            elif "pdf" in (ext.lower() for ext in files.keys()):
                file_ext = 'pdf'

            file_URL = files[file_ext]
            print("File url: ", file_URL)

            target_path = create_target_path(target_data_folder, tr, entry_counter, file_ext)

            download_file(driver, downloaded_data_folder, file_URL, target_path)


        # Add sleeping time for the script every 50 files
        if ((entry_counter != 0) and ((entry_counter % 100) == 0)):
            print("Let's sleep for 3 minutes...")
            time.sleep(180)
            print("Up and running again...")

no_files.close()

driver.close()