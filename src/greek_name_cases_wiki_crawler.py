import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import json
import codecs
import re
import os
from pathlib import Path


def concat_json_files(file_paths):

    ultimate_dict = {}
    for file in file_paths:
        with codecs.open(file, 'r', encoding='utf-8') as f:
            parsed = f.read()
            json_dict = json.loads(parsed)
            ultimate_dict = dict(ultimate_dict, **json_dict)

    return ultimate_dict


def dict_to_file(dict_500, c):

    file_500 = os.path.join(dirpath, str(c)+'.json')
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    with codecs.open(file_500, 'w', encoding='utf-8') as f:
        json.dump(dict_500, f, ensure_ascii=False, indent=4)

    return c


def pad_dict_list(dict_list):

    max_length = 0
    for key in dict_list.keys():
        max_length = max(max_length, len(dict_list[key]))

    for key in dict_list.keys():
        case_length = len(dict_list[key])
        if case_length < max_length:
            dict_list[key] += ' ' * (max_length - case_length)

    return dict_list


def crawl_names(dict_500, domain_URL, url, c, listing_category):
    print('Crawling ', urllib.parse.urljoin(domain_URL, url))
    response = requests.get(urllib.parse.urljoin(domain_URL, url))
    html = response.text  # .content -> response as bytes, .text-> response as unicode/string
    soup = BeautifulSoup(html, "html.parser")

    entries_list = soup.find('div', {'class': 'mw-category'}).find_all('li')

    next_page = soup.find('a', href=True, text='επόμενη σελίδα')

    for entry in entries_list:
        c+=1

        # print(entry)
        name = entry.text
        table_dict = {
            'ενικός':
                {'ονομαστική': '', 'γενική': '',
                 'αιτιατική': '', 'κλητική': ''},
            'πληθυντικός':
                {'ονομαστική': '', 'γενική': '',
                 'αιτιατική': '', 'κλητική': ''}}

        # Get content of name's page
        name_url = entry.find('a')['href']
        response = requests.get(urllib.parse.urljoin(domain_URL,name_url))
        name_html = response.text
        name_soup = BeautifulSoup(name_html, "html.parser")

        if name_soup.find("div", {"class": "NavFrame"}):
            name_soup.find("div", {"class": "NavFrame"}).decompose()

        tables = [table for table in name_soup.find_all('tbody') if
                  any(word in table.text.lower() for word in ['πτώσεις', 'πτώση'])]

        if len(tables) != 0:

            if len(tables) >1:
                print(name, ': tables more than 1\n'+urllib.parse.urljoin(domain_URL,name_url))

                # Choose the right table
                li_tags = name_soup.find_all('li')
                for li_tag in li_tags:
                    if listing_category in li_tag.text.lower():
                        print('Choosing \"', listing_category, '\" section.\n')
                        table = li_tag.find_previous('tbody')
                        break # execute following commands outside this for-loop

                if table != None:

                    # if wrong table is found
                    if not any(word in table.text.lower() for word in ['πτώσεις', 'πτώση']):
                        print(name, ': previous table of li_tag is not the correct one.')
                        dict_500[name] = table_dict
                        continue  # continue with next iteration of for-loop
                else:
                    # if no table is found
                    dict_500[name] = table_dict
                    print(name, ': table ==  None')
                    continue # continue with next iteration of for-loop

            else:
                # take only the first table
                table = tables[0]

            column_names = [th.text.lower().strip() for th in table.find_all('th')]
            # 0 for first row, 1 for notes
            trs = [tr for tr in table.find_all('tr') if len(tr.find_all('td')) > 1]

            # for each row
            for tr in trs:

                row_tds = tr.find_all('td')

                if len(row_tds) != 1: # discard notes at the bottom of tables

                    # discard articles (grammar) that have center alignement
                    row_values = [td.text.strip() for td in row_tds if td.attrs.get('align') != 'center']

                    # if each row has amount of cells equal or less than amount of columns
                    if len(row_values) <= len(column_names):

                        # for each column of the table
                        for i in range(1,len(row_values)):
                            value = row_values[i]
                            # remove digits and * symbol
                            value = re.sub(r'[\d+\*]', '', value)

                            try:
                                if 'δοτική' not in row_values[0].lower(): #discard δοτική
                                    if '&' in value:
                                        value = [v.strip() for v in value.split('&')]
                                    if ' και ' in value:
                                        value = [v.strip() for v in value.split(' και ')]

                                    table_dict[column_names[i]][row_values[0].lower()] = value
                            except:
                                print(name, column_names[i], row_values[0], 'KeyError')

                    else:
                        print(name, ': mismatch len(row_values) == len(column_names)')

        else:
            table_dict = {
                'ενικός':
                    {'ονομαστική': '', 'γενική': '', 'αιτιατική': '', 'κλητική': ''},
                'πληθυντικός':
                    {'ονομαστική': '', 'γενική': '', 'αιτιατική': '', 'κλητική': ''}}

        dict_500[name] = table_dict


        if c%500==0:
            print(str(c)+' entries checkpoint...')
            c = dict_to_file(dict_500, c)
            dict_500 = {}

    if next_page != None:

        return(crawl_names(dict_500, domain_URL, next_page['href'], c, listing_category))

    else:
        #write last dict_500
        c = dict_to_file(dict_500, c)

        return


start_time = time.time()
domain_URL = 'https://el.wiktionary.org'

dirs_urls_dict = {'../out_files/wiki_data/male_name_cases': ['/wiki/Κατηγορία:Ανδρικά_ονόματα_(νέα_ελληνικά)', 'ανδρικό όνομα'],
                  '../out_files/wiki_data/female_name_cases': ['/wiki/Κατηγορία:Γυναικεία_ονόματα_(νέα_ελληνικά)', 'γυναικείο όνομα'],
                  '../out_files/wiki_data/male_surname_cases': ['/wiki/Κατηγορία:Ανδρικά_επώνυμα_(νέα_ελληνικά)', 'ανδρικό επώνυμο'],
                  '../out_files/wiki_data/female_surname_cases': ['/wiki/Κατηγορία:Γυναικεία_επώνυμα_(νέα_ελληνικά)', 'γυναικείο επώνυμο']
}

for dirpath, list in dirs_urls_dict.items():
    dir_name = os.path.basename(dirpath)
    page_url = list[0]
    listing_category = list[1]
    c=0
    dict_500 = {}
    crawl_names(dict_500, domain_URL, page_url, c, listing_category)

    #sort by creation time
    file_paths = sorted(Path(dirpath).iterdir(), key=os.path.getctime)

    ultimate_dict = concat_json_files(file_paths)
    print('Collected '+ str(len(ultimate_dict.keys())) + ' entries in this category.')
    with codecs.open(os.path.join('../out_files/wiki_data/', dir_name+'.json'), 'w', encoding='utf-8') as f:
        json.dump(ultimate_dict, f, ensure_ascii=False, indent=4)

    diff = ((time.time() - start_time)/60)
    print("Lasted --- %s minutes ---" % str(diff))