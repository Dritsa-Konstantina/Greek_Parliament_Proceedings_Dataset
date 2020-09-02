import requests
from bs4 import BeautifulSoup
import re

def crawl_names(page_range, url, outfilepath):

    with open(outfilepath, 'w+', encoding='utf-8') as f:  # encoding for Greek

        for pageNo in range(1, page_range+1):

            print(pageNo)
            response = requests.get(url + str(pageNo))
            html = response.text  # .content -> response as bytes, .text-> response as unicode/string
            soup = BeautifulSoup(html, "html.parser")

            mydiv = soup.find("div", {"class": "main_content_area left"})
            entries = mydiv.find_all('a', {"class": "black2blue"})

            for entry in entries:
                names = ((entry.get_text()).lower()).strip()
                names = re.sub(r"[.,()]", '', names)
                names = re.sub(r"[\s]", ',', names)
                names = names.translate(str.maketrans('άέόώήίϊΐύϋΰ', 'αεοωηιιιυυυ'))  # remove accents
                f.write(names+'\n')

filepaths = ['../out_files/male_names_alternatives_gr.txt', '../out_files/female_names_alternatives_gr.txt']
crawl_names(22, 'https://www.onomatologio.gr/Ονόματα/Ανδρικά?page=', filepaths[0])
crawl_names(21, 'https://www.onomatologio.gr/Ονόματα/Γυναικεία?page=', filepaths[1])

# A file only with the names that have alternatives
with open('../out_files/greek_names_alts_only.txt', 'w+', encoding='utf-8') as f_alt:

    for file in filepaths:
        with open(file, 'r+') as f:
            for line in f.readlines():
                if len(line.split(',')) > 1:
                    f_alt.write(line)

