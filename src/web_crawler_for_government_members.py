# -*- coding: utf-8 -*-
import requests
import pandas as pd
from datetime import datetime as dt
import datetime
import re
from bs4 import BeautifulSoup
from bs4.element import Comment
from collections import defaultdict


def toDatetime(date):

    if date == 'ΣΗΜΕΡΑ':
        date = datetime.date.today()
    else:
        day, month, year = re.split(r'[\.\/-]', date)
        date = dt.strptime(year+'-'+month+'-'+day, '%Y-%m-%d')

    return date


def month_to_number(month):

    months = {'ιανουαριου': '1', 'φεβρουαριου': '2', 'μαρτιου':'3',
              'απριλιου': '4', 'μαιου': '5', 'ιουνιου': '6', 'ιουλιου': '7',
              'αυγουστου': '8', 'σεπτεμβριου': '9', 'οκτωβριου': '10',
              'νοεμβριου': '11', 'δεκεμβριου': '12'}

    return months[month]


def get_date_and_type(event):

    event_parts = [e for e in re.split(r'[\s:\-\.]', event) if e != '']
    day, month, year, event_type = event_parts
    if not month.isnumeric():
        month = month_to_number(month)
    date = dt.strptime(year + '-' + month + '-' + day, '%Y-%m-%d')

    return date, event_type


def remove_notes(content):

    notes_regex = re.compile(r'(ο\s*πρωθυπουργος)|(διορισθηκε)|(διορισθηκαν)')
    new_content = []
    for item in content:
        if notes_regex.search(item):
            continue
        else:
            new_content.append(item)

    return new_content


def tag_visible(element):

    if element.parent.name in ['style', 'script', 'head', 'title', 'meta',
                               '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def soup_to_list(soup):

    texts = soup.find_all(text=True)#.find_all(text=True, recursive=True)
    visible_texts = list(filter(tag_visible, texts))

    return[re.sub(r'\s{2,}', ' ', t) for t in visible_texts if t.strip()!='']


def df_from_gov_table(page_URL):

    response = requests.get(page_URL)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    trs = soup.find("tbody").find_all('tr')
    trs = trs[1:] #skip header

    rows_list = []

    for tr in trs:
        row = [td.text for td in tr.find_all('td')]
        row.append(tr.find('a').get('href'))
        rows_list.append(row)

    df_govs = pd.DataFrame(columns = ['id', 'gov_name', 'date_from', 'date_to', 'gov_url'], data = rows_list)
    df_govs = df_govs.drop(['id'], axis=1)

    df_govs.date_from = df_govs.date_from.apply(lambda x: toDatetime(x))
    df_govs.date_to = df_govs.date_to.apply(lambda x: toDatetime(x))
    df_govs.gov_name = df_govs.gov_name.apply(lambda x: x.lower())

    return df_govs


def text_formatting(text):

    text = re.sub("['’`΄‘́̈]",'', text)
    text = re.sub('\t+' , ' ', text)
    text = text.lstrip()
    text = text.rstrip()
    text = re.sub('\s\s+' , ' ', text)
    text = re.sub('\s*(-|–)\s*' , '-', text) #fix dashes
    text = text.lower()
    text = text.translate(str.maketrans('άέόώήίϊΐiύϋΰ','αεοωηιιιιυυυ')) #remove accents
    text = text.translate(str.maketrans('akebyolruxtvhmnz','ακεβυολρυχτνημνζ')) #convert english characters to greek

    return text

def balanced_parenthesis(myStr):
    stack = []
    for char in myStr:
        if char == '(' or char == ')':
            stack.append(char)
    open = [char for char in stack if char=='(']
    close = [char for char in stack if char==')']
    if len(open) != len(close):
        return False
    else:
        return True


def role_formatting(role):

    if role.startswith('του '):
        role = role.replace(role, role[4:])

    return role


# correct wrongly separated text
def correct_separation(content):

    # Correct unbalanced parentheses
    correct_parenthesis = []
    new_item = ''
    for c in content:

        new_item +=c
        if not balanced_parenthesis(new_item):
            continue
        else:
            correct_parenthesis.append(new_item)
            new_item = ''

    # Remove [1] or [ι]
    content = [c for c in correct_parenthesis if (c.strip()!='[1]' and c.strip()!='[ι]')]

    # Merge wrongly split strings
    merged_items = []
    new_item = ''
    for c in content:
        # Add whitespace if previous string ends with digit
        if endswith_digits_regex.search(new_item):
            new_item = new_item + ' ' + c
        else:
            new_item += c

        if len(new_item)<=3:
            continue
        else:
            merged_items.append(new_item)
            new_item = ''

    # Merge wrongly split date strings
    merged_dates = []
    new_item = ''
    for c in merged_items:

        # Add whitespace if previous string ends with month
        if endswith_month_regex.search(c):
            new_item +=c
            continue
        if endswith_month_regex.search(new_item):
            new_item += ' ' + c
        else:
            new_item += c
        merged_dates.append(new_item)
        new_item = ''

    # Specific problem due to unneeded span tags in tds
    merged_roles = []
    for c in merged_dates:
        if c == 'και ενεργειας' and merged_roles[-1]=='αναπληρωτη υπουργου παραγωγικης ανασυγκροτησης, περιβαλλοντος':
            merged_roles[-1] += ' '+c
        else:
            merged_roles.append(c)

    # Specific problem due to skipped td tags
    final = []
    for c in merged_roles:
        if c == 'αλεξιου τσιπρα πρωθυπουργου':
            final.append('αλεξιου τσιπρα')
            final.append('πρωθυπουργου')
        else:
            final.append(c)

    return final


# e.g. (...) or (π.δ...) or π.δ...(φεκ..) or φεκ..
def remove_presidential_decrees(content):
    decree_in_event = re.compile(r'\(π\.δ(.*?)\)\s*(:|\+)?$')
    parenthesis_start = re.compile(r'^\s*\(')
    parenthesis_end = re.compile(r'\).?\s*$')

    updated_content = []
    for item in content:
        if parenthesis_start.search(item) and parenthesis_end.search(item):
            # do not keep item and continue to next
            continue
        # Specific case
        if item == ':π.δ':
            continue
        if ':' not in item and any(string in item for string in ['π.δ', 'φεκ']):
            continue
        if ':' in item and decree_in_event.search(item):
            item = decree_in_event.sub('', item)

        updated_content.append(item)

    return updated_content


# e.g. 'απο 10.03.2004 μεχρι 19.9.2007', 'κυβερνηση λουκα δ. παπαδημου'
def remove_gov_info(content):

    updated_content = []

    for item in content:
        if any(word in item for word in ['απο ', 'μεχρι ', 'κυβερνηση ', 'υπηρεσιακη κυβερνηση']):
            continue
        else:
            updated_content.append(item)
            
    return updated_content


def clean_up_soup(soup):

    # Remove not needed content. Cannot choose specific div because of malformed html
    soup.find("footer", {"class": "footer"}).decompose()
    soup.find("div", {"class": "comments"}).decompose()
    soup.find("header", {"class": "entry-header"}).decompose()
    soup.find("head").decompose()

    # Replace span tag with its contents to avoid unwanted text separation
    for match in soup.find_all('span'):
        match.unwrap()

    return soup

def assert_correct_roles(df):
    flag = True
    accepted_roles = ['υπουργ', 'υφυπου', 'πρωθυπ', 'αναπλη', 'αντιπρ']
    for index, row in df.iterrows():
        role_initials = row.member_role[:6]
        if role_initials not in accepted_roles:
            flag = False
            print(role_initials)
            print(row)
            print('--------------------------------------------------------------------')

    return flag


def correct_interwined_entries(members, roles):

    m1, m2, r1, r2 = None, None, None, None
    if members == 'γεωργιου ζανιαγεωργιου βερνικου' \
            and roles=='υπουργου οικονομικωνυφυπουργου ναυτιλιας':
        m1 = 'γεωργιου ζανια'
        m2 = 'γεωργιου βερνικου'
        r1 = 'υπουργου οικονομικων'
        r2 = 'υφυπουργου ναυτιλιας'

    if members == 'συμεων κεδικογλου (του βασιλειου)κωνσταντινου τσιαρα' \
            and roles=='υφυπουργου στον πρωθυπουργουφυπουργου εξωτερικων':
        m1 = 'συμεων κεδικογλου(του βασιλειου)'
        m2 = 'κωνσταντινου τσιαρα'
        r1 = 'υφυπουργου στον πρωθυπουργο'
        r2 = 'υφυπουργου εξωτερικων'

    return m1, m2, r1, r2

page_URL = 'http://www.ggk.gov.gr/?page_id=776&sort=time'
df_govs = df_from_gov_table(page_URL)
df_1989_onwards = df_govs[df_govs.date_to >= dt.strptime('1989-07-03', '%Y-%m-%d')]

df_1989_onwards.to_csv('../out_files/governments_1989onwards.csv', header=True, index=False, encoding='utf-8')

endswith_digits_regex = re.compile(r'\d+$')
has_digit_regex = re.compile(r'\d+')

#For specific data correction: υπηρεσιακη κυβερνηση βασιλικης σπ. θανου-χριστοφιλου "27 αυγουστου 2015"
endswith_month_regex = re.compile(r'\s(ιανουαριου|φεβρουαριου|μαρτιου|απριλιου|μαιου|ιουνιου|ιουλιου|αυγουστου|'
                                  r'σεπτεμβριου|οκτωβριου|νομεβριου|δεκεμβριου)$')
activity = defaultdict(list)
all_cases = []

months = []
types = []

rows_list = []

for index, row in df_1989_onwards.iterrows():
    print(row.gov_name)

    html = requests.get(row.gov_url+'&print=1').text #.content -> response as bytes
    html = html.replace(u'\xa0', ' ')
    html = html.replace(u' ', ' ')
    soup = BeautifulSoup(html, "html.parser")

    soup = clean_up_soup(soup)

    # Start formatting content
    content = soup_to_list(soup)

    content = [text_formatting(t) for t in content]
    content = correct_separation(content)

    # Specific correction for wrong data
    if row.gov_name == 'παπανδρεου ανδρεα':
        anaplirosi_index = content.index('αναπληρωσεις:')
        content = content[:anaplirosi_index]

    # Remove not needed information
    content = remove_presidential_decrees(content)
    content = remove_gov_info(content)
    content = remove_notes(content)
    content = [text_formatting(c) for c in content]

    # Create dict  {event:[ [..,..], [..,..], ...]}
    events_per_gov = defaultdict(list)
    added_indexes = []
    last_event = ''
    for index, item in enumerate(content):
        if index not in added_indexes:
            if any(string in item for string in [':','διορισμος', 'παραιτηση', 'παυση', 'απεβιωσε', 'αναπληρωση', 'αναπληρωσεις']):
                last_event = item
            else:
                if last_event!='' and index!=len(content)-1:
                    name = content[index]
                    role = content[index+1]
                    # specific correction for george papandreou government
                    if role == 'θαλασσιων υποθεσεων, νησων και αλιειας':
                        role = 'υφυπουργου θαλασσιων υποθεσεων, νησων και αλιειας'

                    added_indexes.append(index+1)
                    item = [name, role]
                events_per_gov[last_event].append(item)

    events_per_gov.pop('', None)

    # Create initial dataframe
    for event, names_roles in events_per_gov.items():
        date, event_type = get_date_and_type(event)
        for name_role_pair in names_roles:
            member_name = name_role_pair[0]
            role = name_role_pair[1]

            if member_name in ['γεωργιου ζανιαγεωργιου βερνικου', 'συμεων κεδικογλου (του βασιλειου)κωνσταντινου τσιαρα']:

                # specific correction for mistakes in the data in samara's government
                m1,m2,r1,r2 = correct_interwined_entries(member_name, role)
                r1 = role_formatting(r1)
                r2 = role_formatting(r2)
                rows_list.append([date, event_type, m1, r1, row.date_from,row.date_to, row.gov_name])
                rows_list.append([date, event_type, m2, r2, row.date_from,row.date_to, row.gov_name])

            else:
                if not has_digit_regex.search(member_name+role):
                    role = role_formatting(role)
                    rows_list.append([date,event_type, member_name, role, row.date_from, row.date_to, row.gov_name])


df = pd.DataFrame(data = rows_list, columns=['date', 'event', 'member_name',
                                             'member_role', 'gov_date_from', 'gov_date_to', 'gov_name'])

# check if roles are correct
if not assert_correct_roles(df):
    print('Not all entries comply with the proper role format.')
else:
    print('All entries have proper role format.')

print(df.columns)
df.to_csv('../out_files/original_gov_members_data.csv', header=True, index=False, encoding='utf-8')