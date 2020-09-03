import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import json
import pygtrie
import math
import re
import codecs
import pandas as pd
import time
import numpy as np
import datetime
from collections import Counter

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', -1)

# cleaned_ggk_data includes
# date	event	member_name	member_role	gov_date_from	gov_date_to	gov_name	member_first_name	member_last_name	nickname	gender	cleaned_fullname

# cleaned_ggk_members includes
#cleaned_fullname, gender, member_name

# formatted_roles_ggk_data includes
# member_name, roles, gender

def explode(df, column_to_split):

    # all columns except `column_to_split`
    initial_cols =df.columns.to_list()
    other_cols = df.columns.difference([column_to_split], sort=False)

    # calculate length of list equal to number of separate roles
    lens = df[column_to_split].str.len()

    # repeat indexes as many times as the length of each list to split
    idx = np.repeat(df.index.values, lens)

    # populate rows of the other columns based on number of separate roles
    # keep old and repeated index values
    res = pd.DataFrame({
                col:np.repeat(df[col].values, lens)
                for col in other_cols},
                index=idx)

    # append the column with sorted separate roles
    res = res.assign(**{column_to_split:np.concatenate(df[column_to_split].values)})
    res = res[initial_cols]
    # revert the original index order
    res = res.sort_index()

    # drop old index and create new
    res = res.reset_index(drop=True)
    return res

# ASSERTIONS
def assert_filled_gender(df):
    for index, row in df.iterrows():
        if pd.isnull(row['gender']):
            print(row.gender)
    if df['gender'].isnull().values.any()==True:
        print('Warning: some gender values ar NaN for the following member names...')
        print(df['cleaned_fullname'][df['gender'].isnull()])
    else:
        print('All names matched to genders.')
    return

def specific_corrections(df):
    d3 = {'στεφανος μανου': 'στεφανος μανος', 'αθανασιος νακου':'αθανασιος νακος',
         'αλεξανδρος κοντου' : 'αλεξανδρος κοντος', 'αναργυρος φατουρου' : 'αναργυρος φατουρου',
         'ανδρεας λοβερδου' : 'ανδρεας λοβερδος', 'ανδρεας λυκουρεντζου' : 'ανδρεας λυκουρεντζος',
         'ανδρεας ξανθου' : 'ανδρεας ξανθος', 'γεωργιος αγαπητου' : 'γεωργιος αγαπητος',
         'γεωργιος βερνικου' : 'γεωργιος βερνικος', 'γεωργιος ζαββου' : 'γεωργιος ζαββος',
         'γεωργιος κατρουγκαλου' : 'γεωργιος κατρουγκαλος', 'γεωργιος κουμαντου' : 'γεωργιος κουμαντος',
         'γεωργιος ντολιου' : 'γεωργιος ντολιος', 'γεωργιος ορφανου' : 'γεωργιος ορφανος',
         'γεωργιος παπασταμκου' : 'γεωργιος παπασταμκος', 'γεωργιος ρωμαιου' : 'γεωργιος ρωμαιος',
         'γεωργιος στυλιου' : 'γεωργιος στυλιος', 'γρηγοριος γιανναρου' : 'γρηγοριος γιανναρος',
         'δημητριος αλαμπανου' : 'δημητριος αλαμπανος', 'δημητριος θανου' : 'δημητριος θανος',
         'δημητριος καμμενου' : 'δημητριος καμμενος', 'δημητριος κρεμαστινου' : 'δημητριος κρεμαστινος',
         'δημητριος λιακου' : 'δημητριος λιακος', 'δημητριος φατουρου' : 'δημητριος φατουρος',
         'διονυσιος λιβανου' : 'διονυσιος λιβανος', 'ελευθεριος κρετσου' : 'ελευθεριος κρετσος',
         'ευαγγελος λιβιερατου' : 'ευαγγελος λιβιερατος', 'ευαγγελος μαλεσιου' : 'ευαγγελος μαλεσιος',
         'ευκλειδης τσακαλωτου' : 'ευκλειδης τσακαλωτος', 'ηλιας μοσιαλου' : 'ηλιας μοσιαλος',
         'θεοδωρος γκαμαλετσου' : 'θεοδωρος γκαμαλετσος', 'θεοδωρος δαμιανου' : 'θεοδωρος δαμιανος',
         'θεοδωρος κατριβανου' : 'θεοδωρος κατριβανος', 'θεοδωρος κολιοπανου' : 'θεοδωρος κολιοπανος',
         'θεοδωρος λιβανιου' : 'θεοδωρος λιβανιος', 'θεοδωρος παγκαλου' : 'θεοδωρος παγκαλος',
         'ιωαννης ανδριανου' : 'ιωαννης ανδριανος', 'ιωαννης γιαγκου' : 'ιωαννης γιαγκος',
         'ιωαννης κουτσουκου' : 'ιωαννης κουτσουκος', 'ιωαννης παναρετου' : 'ιωαννης παναρετος',
         'κωνσταντινος βρεττου' : 'κωνσταντινος βρεττος', 'κωνσταντινος κουκοδημου' : 'κωνσταντινος κουκοδημος',
         'λουκας παπαδημου' : 'λουκας παπαδημος', 'παυλος γερουλανου' : 'παυλος γερουλανος',
         'μιχαηλ γαλενιανου' : 'μιχαηλ γαλενιανος', 'νεκταριος σαντορινιου' : 'νεκταριος σαντορινιος',
         'νικολαος κλειτου' : 'νικολαος κλειτος', 'νικολαος-λεανδρος λιναρδατου' : 'νικολαος-λεανδρος λιναρδατος',
         'νικολαος-μιχαηλ αλιβιζατου' : 'νικολαος-μιχαηλ αλιβιζατος', 'παναγιωτης δελημητσου' : 'παναγιωτης δελημητσος',
         'παναγιωτης καμμενου' : 'παναγιωτης καμμενος', 'παναγιωτης πικραμμενου' : 'παναγιωτης πικραμμενος',
         'πετρος-παυλος αλιβιζατου' : 'πετρος-παυλος αλιβιζατος', 'σπυριδων ταλιαδουρου' : 'σπυριδων ταλιαδουρος',
         'σωκρατης φαμελλου' : 'σωκρατης φαμελλος', 'σταυρος μπενου' : 'σταυρος μπενος',
         'φιλιππος πετσαλνικου' : 'φιλιππος πετσαλνικος', 'φραγκουλης φραγκου' : 'φραγκουλης φραγκος',
         'χρηστος ροκοφυλλου' : 'χρηστος ροκοφυλλος', 'χρηστος-γεωργιος σκερτσου' : 'χρηστος-γεωργιος σκερτσος',
          r'\bλιασκου\b': 'λιασκος', r'\bευρυπιδης\b':'ευριπιδης', r'\bιωαννης βαρουφακης\b': 'γιανης βαρουφακης',
          r'\bζουραρις\b': 'ζουραρης'

          }

    df['cleaned_fullname'] = df['cleaned_fullname'].replace(d3, regex=True)


    return(df)

# def changed_ministry_names():
#     παπανδρεου ανδρεα, 1993-10-13,

def first_name_formatting(df):

    # Convert full strings to genitive case
    d = {r'\bελπιδα\b': 'ελπιδας', r'\bαθανασια\b': 'αθανασιας', r'\bφωτεινη\b':'φωτεινης',
         r'\bιωαννου\b':'ιωαννη', r'\bαικατερινη\b':'αικατερινης', r'\bγεωργιος\b':'γεωργιου',
         r'\bπαναγιωτου\b':'παναγιωτη', r'\bξενοφωντος\b':'ξενοφωντα', r'\bβυρωνος\b': 'βυρωνα',
         r'\bπαντελεημονος\b': 'παντελεημονα', r'\bθεανους\b':'θεανως', r'\bσπυριδωνος\b|\bσπυριδων\b':'σπυριδωνα',
         r'\bσοφια\b': 'σοφιας', r'\bπαρασκευη\b': 'παρασκευης', r'\bοδυσσεας\b': 'οδυσσεα',
         r'\bπαναγιωτης\b': 'παναγιωτη', r'\bολγα\b': 'ολγας', r'\bμηχαηλ\b': 'μιχαηλ',
         r'\bλουκια-ταρσιτσα\b':'λουκιας-ταρσιτσας', r'\bμαρια\b': 'μαριας',
         r'\bκωνσταντινα\b': 'κωνσταντινας', r'\bαννα\b':'αννας', r'\bαλκηστις\b': 'αλκηστιδος',
         r'\bαδωνι\b': 'αδωνιδος', r'\bτρυφωνα\b': 'τρυφωνος', r'\bπροκοπη\b':'προκοπιου',
         r'\bευρυπιδης\b':'ευριπιδης', r'\bαντωνη\b':'αντωνιου', r'\bανασταση\b': 'αναστασιου'

         }
    # regex False exact full string match,
    # regex True substrings replaced unless use \bstring\b in first parenthesis. regex only in first parenthesis
    df['member_first_name'] = df['member_first_name'].replace(d, regex=True)

    return(df)

def name_formatting_dataframe(df):
    df['member_name'] = df['member_name'].str.replace(r'\x96', '-')
    df['member_name'] = df['member_name'].str.replace(r'\s+\-\s+', '-')

    # Add whitespace before parenthesis. (\S) matches any non-whitespace character.
    df['member_name'] = df['member_name'].str.replace(r"(\S)\(",
                                                                r'\1 (')
    # remove father's name in parenthesis
    regex_fatherName = re.compile('(^.*)(\s\((του)\s.*?\)$)')
    df['member_name'] = df['member_name'].str.replace(regex_fatherName, r'\1')

    # rearrange order of string parts with capture groups. move parentheses to end of name
    regex_parenthesis = re.compile('(^.*)(\s\(.*?\))(.*$)')
    df['member_name'] = df['member_name'].str.replace(
        regex_parenthesis, r'\1\3\2')

    df['member_name'] = df['member_name'].str.replace(
        r'( γ\. )|( α\. )|( οθ\. )|( συζ\.δημητριου )|( σπ\. )|( σπ\.)', ' ')
    df['member_name'] = df['member_name'].str.replace(
        '\(πρωθυπουργου \)', '')
    df['member_name'] = df['member_name'].str.replace(
        '\(πρωθυπουργου \)', '')
    df['member_name'] = df['member_name'].str.replace(
        r'αποστολ\.|αποστ\.|αποστολουυ', 'αποστολου')

    # Convert substrings to genitive case and make corrections
    d1 = {r'\(βασω\)':'(βασως)', r'\(κελλυ\)':'(κελλυς)', r'\bκαμμενο\b':'καμμενου', r'\bγαλελιανου\b':'γαλενιανου',
          r'\bκαχριμακη\b':'καρχιμακη', r'\bξενογιαννακο\-πουλου\b':'ξενογιαννακοπουλου',
          r'\bβασιλικη παπανδρεου\b':'βασιλικης παπανδρεου', r'\bσπηλιοτοπουλου\b':'σπηλιωτοπουλου',
          r'\bκαλατζακου\b':'καλαντζακου', r'\bγενηματα\b':'γεννηματα',
          r'\bψαρουδας\b':'ψαρουδα'
          }
    df['member_name'] = df['member_name'].replace(d1, regex=True) # replace substring first parenthesis accepts regex, second accepts string so we don't need to escape the parenthesis symbol


    # Convert full strings to genitive case
    d2 = {'τζαννη τζανετακη': 'τζαννη τζαννετακη', 'φανη παλλη-πετραλια': 'φανης παλλη-πετραλια',
         'αναστασιο λιασκο':'αναστασιου λιασκου','αμαλια-μαρια μερκουρη (μελινα)':'αμαλιας-μαριας μερκουρη (μελινας)',
         'αγγελικη γκερεκου':'αγγελικης γκερεκου', 'αγγελικη-ευφροσυνη κιαου':'αγγελικης-ευφροσυνης κιαου-δημακου',
         'αλεξανδρος χαριτσης': 'αλεξανδρου χαριτση', 'γεωργιου σουλφια':'γεωργιου σουφλια',
         'ιωαννη ανδριανο':'ιωαννη ανδριανου', 'νικολαου λιναρδατου':'νικολαου-λεανδρου λιναρδατου',
         'καλλιοπης μπουρδαρα':'καλλιοπης μπουρδαρα (κελλυς)', 'ευαγγελου βανιζελου':'ευαγγελου βενιζελου',
          'βασιλικης παπανδρεου': 'βασιλικης παπανδρεου (βασως)', 'αντωνιος ρουπακιωτης':'αντωνιου ρουπακιωτη',
          'ιωαννη λιαππη':'ιωαννη λιαπη', 'ιωαννη κεφαλλογιαννη':'ιωαννη κεφαλογιαννη',
          'αναστασιου λιασκος': 'αναστασιου λιασκου', 'φωτη κουβελη':'φωτιου-φανουριου κουβελη'
         }

    df['member_name'] = df['member_name'].replace(d2, regex=False) # regex False exact full string match, regex True substrings replaced

    df['member_name'] = df['member_name'].str.replace('κων/νου',
                                                                'κωνσταντινου')
    df['member_name'] = df['member_name'].str.replace('ανασταστιου',
                                                                'αναστασιου')
    df['member_name'] = df['member_name'].str.replace(
        'νικολ\.φωτιου χατζημιχαλη', 'νικολαου-φωτιου χατζημιχαλη')
    df['member_name'] = df['member_name'].str.replace(
        r'(μαρια-κολλια τσαρουχα)|(μαριας κολλια τσαρουχα)',
        'μαριας κολλια-τσαρουχα')
    df['member_name'] = df['member_name'].str.replace(
        r'(αποστολου-αθαν\. τσοχατζοπουλου)|(αποστολου-αθανας\. τσοχατζοπουλου)|'
        r'(αποστολουυ-αθαν\.τσοχατζοπουλου)|(αποστολουυ-αθανασιου τσοχατζοπουλου)|'
        r'(αποστολου-αθαν\.τσοχατζοπουλου)',
        'αποστολου-αθανασιου τσοχατζοπουλου')

    df['member_name'] = df['member_name'].str.strip()
    # print(df['member_name'].to_list())

    return(df)

def format_member_role(role):
    # print(role)

    convert_roles = {'πρωθυπουργου':'πρωθυπουργος', 'υπουργου':'υπουργος',
                     'αναπληρωτη':'αναπληρωτης', 'αναπληρωτριας':'αναπληρωτης',
                     'αναπληρωτου': 'αναπληρωτης', 'υπουργουυγειας,':'υπουργος υγειας ',
                     'υφυπουργου':'υφυπουργος', 'υφυπουγου':'υφυπουργος',
                     'αντιπροεδρου':'αντιπροεδρος'}

    parts = role.split()
    for i, part in enumerate(parts):
        if part in convert_roles.keys():
            parts[i] = convert_roles[part]

    new_role = ' '.join(parts)
    new_role = re.sub(r',[^\s]', ', ', new_role)
    new_role = re.sub(',', ' ', new_role)
    new_role = re.sub(r'\s\s+', ' ', new_role)

    new_role = new_role.replace('πε.χω.δε', 'περιβαλλοντος χωροταξιας και δημοσιων εργων')
    new_role = new_role.replace('υπουργος βιομηχανιας ενεργειας και τεχνολογιας και εμποριου',
                                'υπουργος βιομηχανιας ενεργειας και τεχνολογιας και υπουργος εμποριου')
    new_role = new_role.replace('\x91', '')
    new_role = new_role.replace('μ.μ.ε', 'μεσων μαζικης ενημερωσης')
    new_role = new_role.replace('διιοικησης', 'διοικησης')
    new_role = new_role.replace('δημοσια ταξης', 'δημοσιας ταξης')
    new_role = new_role.replace('εσωτερικων εσωτερικων', 'εσωτερικων')
    new_role = new_role.replace('υπουργος αναπληρωτης', 'αναπληρωτης υπουργος')
    new_role = re.sub(r'δημ.διοικησης|ημ.διοικησης|δημ. διοικησης', 'δημοσιας διοικησης', new_role)
    new_role = new_role.replace(' ημοσιας', ' δημοσιας')
    new_role = new_role.replace('εςωτερικων', 'εσωτερικων')
    new_role = new_role.replace('δημο-σιων', 'δημοσιων')
    new_role = new_role.replace('&', 'και')
    new_role = new_role.replace(' π εριβαλλοντος', ' περιβαλλοντος')
    new_role = new_role.replace('παιδειας και θρησκευματων πολιτισμου και αθλητισμου',
                                'παιδειας θρησκευματων πολιτισμου και αθλητισμου')
    new_role = new_role.replace('πολιτιςμου', 'πολιτισμου')
    new_role = new_role.replace('μακεδονιας και θρακης', 'μακεδονιας-θρακης')
    new_role = new_role.replace('χαρτο-φυλακιο', 'χαρτοφυλακιο')
    new_role = new_role.replace('περιβαλλοντοςκαι', 'περιβαλλοντος και')
    new_role = new_role.replace('ενη-μερωσης', 'ενημερωσης')
    new_role = new_role.replace('μακεδονιας θρακης', 'μακεδονιας-θρακης')
    new_role = new_role.replace('ανθρωπινωνδικαιωματων', 'ανθρωπινων δικαιωματων')
    new_role = new_role.replace('αναπληρωτης υπουργος ναυτιλιας και νησιωτικης πολιτικης αγροτικης αναπτυξης και τροφιμων',
                                'αναπληρωτης υπουργος ναυτιλιας και νησιωτικης πολιτικης')
    new_role = new_role.replace('τεχνολο-γιας', 'τεχνολογιας')

    new_role = new_role.replace('γεωγιας', 'γεωργιας')
    new_role = re.sub(r'\s\s+', ' ', new_role)
    new_role = re.sub(r'(,|\.)$', '', new_role)
    new_role = new_role.strip()
    # print(new_role)
    return new_role

def correct_specific_roles(df, name, role_before, role_after, date, gov_date_from):

    mask = (df.cleaned_fullname == name) \
           & (df.member_role == role_before) \
           & (df.date == date) \
           & (df.gov_date_from == gov_date_from)
    # print(df.loc[mask, 'member_role'])
    df.loc[mask, 'member_role'] = role_after
    return df

def correct_specific_events(df, name, role, event_before, event_after, date, gov_date_from):

    mask = (df.cleaned_fullname == name) \
           & (df.event == event_before) \
           & (df.date == date) \
           & (df.member_role == role) & \
           (df.gov_date_from == gov_date_from)
    df.loc[mask, 'event'] = event_after
    return df

def text_formatting(text):
    text = re.sub("['’`΄‘́̈]",'', text)
    text = re.sub('\t+' , ' ', text) #replace one or more tabs with one space
    text = text.lstrip() #remove leading spaces
    text = text.rstrip() #remove trailing spaces
    text = re.sub('\s\s+' , ' ', text) #replace more than one spaces with one space
    text = re.sub('\s*(-|–)\s*' , '-', text) #fix dashes
    text = text.lower()
    text = text.translate(str.maketrans('άέόώήίϊΐiύϋΰ','αεοωηιιιιυυυ')) #remove accents
    text = text.translate(str.maketrans('akebyolruxtvhmnz','ακεβυολρυχτνημνζ')) #convert english characters to greek
    return(text)

def json_file_to_chartrie(json_file):

    with codecs.open(json_file, 'r+', encoding='utf-8') as f:
        parsed = f.read()
        formatted_text = text_formatting(parsed)
        json_dict = json.loads(formatted_text)

    trie = pygtrie.CharTrie()

    for key, value in json_dict.items():
        trie[key] = value

    return(trie)

def find_nominative_and_gender(search_term, gender, tries, surname_search = False):

    if pd.isnull(search_term):
        return(search_term, gender)
    else:
        if surname_search == False or gender=='male' or pd.isnull(gender):
            # print(search_term)

            parts_of_name = {}

            for part in search_term.split('-'):

                # return the same if nothing is found
                matched_name, matched_gender = part, gender

                first_half = part[0:(math.ceil(len(part) / 2))]
                # print('first_half ', first_half)

                foundintrie = False

                for trie_gender, trie in tries.items():

                    if trie.has_subtrie(first_half):
                        # if part == 'σπυριδωνα':
                        #     print('***************')
                        for name, info in trie.iteritems(prefix=first_half):
                            if len(name) > ((2 * len(first_half)) + 2) or name=='νικολαους':
                                continue
                            # if part=='σπυριδωνα':
                            #     print(name)

                            if type(info['ενικος']['γενικη']) == str and part == info['ενικος']['γενικη']:

                                matched_name, matched_gender = name, trie_gender
                                # if part == 'σπυριδωνα':
                                #     print('yes')
                                #     print(matched_name)
                                foundintrie = True
                                break
                            elif type(info['ενικος']['γενικη']) == list and part in info['ενικος']['γενικη']:
                                matched_name, matched_gender = name, trie_gender
                                # if part == 'σπυριδωνα':
                                #     print('yesss')
                                #     print(matched_name)
                                foundintrie = True
                                break

                if surname_search == True and foundintrie == False: #if it is male surname
                    # print(part)
                    if not (part.endswith('ου') or (part[-1] in ['ς', 'λ', 'τ', 'κ'])):
                        matched_name = part+'ς'
                # if '-' in search_term:
                #     print(matched_name)
                parts_of_name[matched_name] = matched_gender

            # if all genders are the same
            genders = list(set([g for g in parts_of_name.values() if not pd.isnull(g)]))
            if len(genders)<=1:
                matched_name = '-'.join(parts_of_name.keys())
                # sets don't support indexing or slicing
                matched_gender = genders[0] if len(genders)==1 else np.nan
                # if part =='αλεξανδρος':
                #     print(matched_gender, matched_name)
            else:
                print('error with genders of name parts of ', search_term)
                print(parts_of_name)

        # if we are searching for the nominative of a female surname, it is the same
        else:
            matched_name, matched_gender = search_term, gender
        # if not pd.isnull(gender) and not pd.isnull(matched_gender):
        #     if gender!= matched_gender:
        #         print(search_term, gender, matched_gender)
        # if search_term=='σταυρου':
        #     print(search_term, matched_name, matched_gender)
        return matched_name, matched_gender

def assert_balanced_events_for_each_role(df):
    start_events = ['διορισμος', 'αρχη_κυβερνησης']
    end_events = ['παραιτηση', 'παυση', 'απεβιωσε', 'last_script_run', 'τελος_κυβερνησης']
    balanced = True

    for name, subdf in df.groupby(['cleaned_fullname',
                                   'gov_date_from', 'member_role']):  # , 'gov_date_to', 'member_role'
        if True:
            # if (subdf['gov_name'].iloc[0]) != 'μητσοτακη κυριακου':

            # subdf = subdf.sort_values(by='date', ascending=True)

            start_events_subdf = subdf.loc[subdf.event.isin(start_events)]
            end_events_subdf = subdf.loc[(subdf.event.isin(end_events))]

            if start_events_subdf.shape[0] != end_events_subdf.shape[0]:

                # print(subdf.sort_values(by='date', ascending=True))
                print(subdf)
                print()
                balanced = False

    return balanced


# PREPARE DATAFRAME
df = pd.read_csv('../out_files/original_gov_members_data.csv', encoding='utf-8')
# print(df.columns) #['date', 'event', 'member_name', 'member_role', 'gov_date_from', 'gov_date_to', 'gov_name']

# df.fillna(value=np.nan, inplace=True)
df = name_formatting_dataframe(df)

# for index, row in df.iterrows():
#     if len((row.member_name).split(' ')) >3:
#         print(row.member_name)

df[['member_first_name','member_last_name', 'nickname']] = df['member_name'].str.split(" ", expand=True).fillna(value=np.nan)


df = first_name_formatting(df)
# print(df['member_name'].to_list())
# time.sleep(100000)
df['nickname'] = df['nickname'].str.replace(r'[\(\)]', '')
df['gender'] = np.nan


# CREATE TRIES FOR NAME SEARCH
male_name_trie = json_file_to_chartrie('../out_files/wiki_data/male_name_cases_populated.json')
female_name_trie = json_file_to_chartrie('../out_files/wiki_data/female_name_cases_populated.json')
male_surname_trie = json_file_to_chartrie('../out_files/wiki_data/male_surname_cases_populated.json')
#female_surname_trie = json_file_to_chartrie('../out_files/wiki_data/female_surname_cases_populated.json')

name_tries = {'male':male_name_trie, 'female':female_name_trie}
surname_tries = {'male': male_surname_trie} # because female surnames don't change between cases

# FIND NOMINATIVE CASE AND GENDER
# Create df because only on df (not series/column) you can apply a custom function that returns two variables
# first_name_gender_df = pd.DataFrame(data = df['member_first_name'].copy(), columns=['member_first_name'])

first_name_gender_df = df['member_first_name'].to_frame().join(df['gender'])
df[['member_first_name', 'gender']] = first_name_gender_df.apply(lambda x: find_nominative_and_gender(x['member_first_name'], x['gender'], name_tries, surname_search=False), axis=1, result_type="expand")


nickname_gender_df = df['nickname'].to_frame().join(df['gender'])
df[['nickname', 'gender']] = nickname_gender_df.apply(lambda x: find_nominative_and_gender(x['nickname'], x['gender'], name_tries, surname_search=False), axis=1, result_type="expand")


df["nickname"] = df["nickname"].apply(lambda x: '('+x+')' if not pd.isnull(x) else '')

last_name_gender_df = df['member_last_name'].to_frame().join(df['gender'])
df[['member_last_name', 'gender']] = last_name_gender_df.apply(lambda x: find_nominative_and_gender(x['member_last_name'], x['gender'], surname_tries, surname_search=True), axis=1, result_type="expand")

# JOIN
name_cols = ['member_first_name', 'member_last_name', 'nickname'] #
df['cleaned_fullname'] = df[name_cols].agg(' '.join, axis=1).str.strip()#.replace(r'\s+', ' ')
df = specific_corrections(df)

df['member_role'] = df['member_role'].apply(format_member_role)

# specific corrections
#----------------
# role corrections before "exploding" roles, due to mistaken data
df = correct_specific_roles(df, 'τζαννης τζαννετακης', 'υπουργος εξωτερικων και τουρισμου',
                       'υπουργος τουρισμου', '1989-07-03', '1989-07-02')
df = correct_specific_roles(df, 'γεωργιος γεννηματας', 'υπουργος εθνικης οικονομιας και οικονομικων',
                       'υπουργος εθνικης οικονομιας και υπουργος οικονομικων', '1993-10-13', '1993-10-13')
df = correct_specific_roles(df, 'γεωργιος κοντογεωργης', 'υπουργος εθνικης οικονομιας και τουρισμου',
                       'υπουργος εθνικης οικονομιας και υπουργος τουρισμου','1989-10-12', '1989-10-12')
df = correct_specific_roles(df, 'στεφανος μανος', 'υπουργος εθνικης οικονομιας και οικονομικων',
                       'υπουργος εθνικης οικονομιας και υπουργος οικονομικων','1993-10-13', '1990-04-11')
df = correct_specific_roles(df, 'γιαννος παπαντωνιου', 'υπουργος εθνικης οικονομιας και οικονομικων',
                       'υπουργος εθνικης οικονομιας και υπουργος οικονομικων','2000-04-13', '1996-09-25')
#----------------

# look ahead assertion in regex
df['member_role'] = df['member_role'].str.split(r'\s(?=και υφυπουργ|και υπουργ|και αναπληρωτ|και πρωθυπουργ|και αντιπροεδρ)')
df = explode(df, 'member_role')
df['member_role'] = df['member_role'].str.replace(r'^και\s', '')

# specific corrections
#----------------

# missing rows
new_rows = [ # date, event, member_name, member_role, gov_date_from, gov_date_to,
            # gov_name, first, last, gender, nickname, cleaned_fullname
    ['2012-03-27', 'παραιτηση', 'φωτεινης γεννηματα', 'αναπληρωτης υπουργος εσωτερικων',
     '2011-11-11', '2012-05-17', 'παπαδημου λουκα δ.', #'υπηρεσιακη/μεταβατικη κυβερνηση',
     'φωτεινη', 'γεννηματα', np.nan, 'female', 'φωτεινη γεννηματα'],
    ['1996-09-25', 'παραιτηση', 'σημιτη κωνσταντινου', 'πρωθυπουργος',
     '1996-01-22', '1996-09-25', 'κωνσταντινου σημιτη', #'πανελληνιο σοσιαλιστικο κινημα',
     'κωνσταντινος', 'σημιτης',  np.nan, 'male', 'κωνσταντινος σημιτης'],
    ['1999-09-14', 'απεβιωσε', 'γιαννου κρανιδιωτη', 'αναπληρωτης υπουργος εξωτερικων',
     '1996-09-25', '2000-04-13', 'σημιτη κωνσταντινου', #'πανελληνιο σοσιαλιστικο κινημα',
     'γιαννος', 'κρανιδιωτης', np.nan,'male', 'γιαννος κρανιδιωτης'],
    ['2012-06-21', 'τελος_κυβερνησης', 'γεωργιου ζανια', 'υπουργος οικονομικων',
     '2012-05-17', '2012-06-21', 'πικραμμενου παναγιωτη οθ. (υπηρεσιακη)',#'υπηρεσιακη/μεταβατικη κυβερνηση',
     'γεωργιος', 'ζανιας', np.nan, 'male', 'γεωργιος ζανιας'],
    ['2012-06-21', 'αρχη_κυβερνησης', 'γεωργιου ζανια', 'υπουργος οικονομικων',
     '2012-06-21','2015-01-26','σαμαρα κ. αντωνιου',#'νεα δημοκρατια',
     'γεωργιος', 'ζανιας', np.nan, 'male',  'γεωργιος ζανιας'],
    ['2012-06-21', 'αρχη_κυβερνησης', 'γεωργιου ζανια', 'υπουργος οικονομικων',
     '2012-06-21','2015-01-26','σαμαρα κ. αντωνιου',#'νεα δημοκρατια',
     'γεωργιος', 'ζανιας', np.nan, 'male',  'γεωργιος ζανιας']
]
rows_df = pd.DataFrame(new_rows, columns = df.columns)
df = df.append(rows_df, ignore_index=True)


# FIX CHANGE IN MEMBER ROLES BASED ON "Ν. 1943/1991" https://gslegal.gov.gr/?p=1304
df['gov_date_from']= pd.to_datetime(df['gov_date_from'])
df['date']= pd.to_datetime(df['date'])

gov_date_from = datetime.datetime.strptime('1990-04-11', '%Y-%m-%d')
event_date = datetime.datetime.strptime('1991-04-11', '%Y-%m-%d')

ministers_without_portfolio_1990 = df.loc[(df.gov_date_from == gov_date_from) & (df.member_role=='υπουργος χωρις χαρτοφυλακιο')].copy()

for name, subdf in ministers_without_portfolio_1990.groupby(['cleaned_fullname']):
    if subdf.shape[0] == 1 and subdf['event'].iloc[0] == 'διορισμος':
        copy = subdf.copy()
        new_subdf = copy.append(copy, ignore_index=True)
        # we can use .at because index is reset
        new_subdf['event'].at[0] = 'παραιτηση'
        new_subdf['date'].at[0] = (event_date - datetime.timedelta(days=1)).date()
        new_subdf['event'].at[1] = 'διορισμος'
        new_subdf['date'].at[1] = event_date
        new_subdf['member_role'].at[1] = 'υπουργος επικρατειας'

        df = pd.concat([df, new_subdf], ignore_index=True)
    else:
        print('Error in minsters without portfolio in 1990.')

# event corrections due to mistaken data
df = correct_specific_events(df, 'γεωργιος κουμουτσακος', 'αναπληρωτης υπουργος μεταναστευσης και ασυλου',
                             'παραιτηση', 'διορισμος', '2020-01-15', '2019-07-08')
df = correct_specific_events(df, 'παναγιωτης μηταρακης', 'υπουργος μεταναστευσης και ασυλου',
                             'παραιτηση', 'διορισμος', '2020-01-15', '2019-07-08')
df = correct_specific_events(df, 'κωνσταντινος κουκοδημος', 'υφυπουργος παιδειας και θρησκευματων',
                             'διορισμος', 'παραιτηση', '2014-09-02', '2012-06-21')

# corrections/changes due to renaming of ministries during a term of office
# keeping the first name of the ministry
df = correct_specific_roles(df, 'αναστασιος λιασκος', 'υφυπουργος τουριστικης αναπτυξης',
                       'υφυπουργος τουρισμου', '2006-02-15', '2004-03-10')

df = correct_specific_roles(df, 'ανδρεας ξανθος', 'αναπληρωτης υπουργος υγειας',
                        'αναπληρωτης υπουργος υγειας και κοινωνικων ασφαλισεων','2015-08-27', '2015-01-26')

df = correct_specific_roles(df, 'αποστολος φωτιαδης', 'υφυπουργος οικονομιας και οικονομικων',
                            'υφυπουργος οικονομικων', '2004-03-10', '2000-04-13')

df = correct_specific_roles(df, 'γεωργιος φλωριδης', 'υφυπουργος οικονομιας και οικονομικων',
                            'υφυπουργος οικονομικων', '2003-07-07', '2000-04-13')

df = correct_specific_roles(df, 'δημητριος αβραμοπουλος', 'υπουργος τουριστικης αναπτυξης',
                       'υπουργος τουρισμου','2006-02-15', '2004-03-10')

df = correct_specific_roles(df, 'δημητριος στρατουλης', 'αναπληρωτης υπουργος υγειας',
                        'αναπληρωτης υπουργος υγειας και κοινωνικων ασφαλισεων','2015-03-21', '2015-01-26')

df = correct_specific_roles(df, 'θεανω φωτιου', 'αναπληρωτης υπουργος εργασιας κοινωνικης ασφαλισης και κοινωνικης αλληλεγγυης',
                        'αναπληρωτης υπουργος εργασιας και κοινωνικης αλληλεγγυης','2015-08-27', '2015-01-26')

df = correct_specific_roles(df, 'χρηστος παχτας', 'υφυπουργος οικονομιας και οικονομικων',
                       'υφυπουργος εθνικης οικονομιας','2004-01-26', '2000-04-13')

df = correct_specific_roles(df, 'φιλιππος σαχινιδης', 'υφυπουργος οικονομικων',
                       'υφυπουργος οικονομιας ανταγωνιστικοτητας και ναυτιλιας','2011-06-17', '2009-10-06')

df = correct_specific_roles(df, 'παναγιωτης σκουρλετης', 'υπουργος εργασιας κοινωνικης ασφαλισης και κοινωνικης αλληλεγγυης',
                       'υπουργος εργασιας και κοινωνικης αλληλεγγυης','2015-07-18', '2015-01-26')

df = correct_specific_roles(df, 'παναγιωτης κουρουμπλης', 'υπουργος υγειας',
                       'υπουργος υγειας και κοινωνικων ασφαλισεων','2015-08-27', '2015-01-26')

#----------------

assert_filled_gender(df)
df.drop_duplicates(inplace=True)

# FIX LAST GOVERNMENT ROLE ENDING DATES
last_gov_events = df.loc[(df.gov_date_from==df.gov_date_from.max())].copy()
for name, subdf in last_gov_events.groupby(['cleaned_fullname', 'member_role']):
    if subdf.shape[0] == 1 and subdf['event'].iloc[0] == 'διορισμος':
        copy = subdf.copy()
        # we use .iat because index is not reset
        copy['event'].iat[0] = 'last_script_run'
        copy['date'].iat[0] = copy['gov_date_to'].iat[0]
        df = pd.concat([df, copy], ignore_index=True)


for name, subdf in df.groupby(['cleaned_fullname', 'gov_date_from']):
    freqs = Counter(subdf['member_role'].to_list())
    # print(freqs)
    odd_roles = [role for role in freqs.keys() if freqs[role] == 1]
    if len(odd_roles) == 2:
        matched_events = subdf.loc[(subdf['member_role'].isin(odd_roles))]
        # print(matched_events)
        matched_events = matched_events.sort_values(by='date', ascending=True)
        indexes = matched_events.index
        # print(indexes)
        # print(df.loc[(df.index==indexes[0]) & (df.event=='διορισμος'),'member_role'].values)
        # print(type(df.loc[(df.index==indexes[0]) & (df.event=='διορισμος'),'member_role']))

        # for the index of resignation, change the role to that of the appointment
        df.loc[(df.index==indexes[1]) & (df.event=='παραιτηση'),'member_role'] = df.loc[(df.index==indexes[0]) & (df.event=='διορισμος'),'member_role'].values[0]
        # print(indexes)

    elif len(odd_roles) != 2 and len(odd_roles) != 0:
        print('weird')

# group by cleaned_fullname gov_date_from balanced events

df['date']= pd.to_datetime(df['date'])
df = df.sort_values(by='date', ascending=True)#.reset_index(drop=True) #,inplace=True
df.drop_duplicates(inplace=True)
df.to_csv('../out_files/cleaned_gov_members_data.csv', encoding='utf-8', index=False)

# # Save names in separate file
# df_names = df['cleaned_fullname'].to_frame().join(df['gender']).join(df['member_name'])
# df_names.drop_duplicates(inplace=True)
# df_names = df_names.sort_values(['gender', 'cleaned_fullname'], ascending=[True, True])
# print(df_names.columns)
# df_names.to_csv('../out_files/cleaned_ggk_members.csv', encoding='utf-8', index=False)

df = pd.read_csv('../out_files/cleaned_gov_members_data.csv', encoding='utf-8')

# balanced = assert_balanced_events_for_each_role(df)
# print('Are all events balanced in the dataset? ', balanced)

final_list = []

#change format of date e.g. from 2001-01-27 to 27/01/2001
def format_date_column(date):
    year, month, day = date.split('-')
    new_date = day+'/'+month+'/'+year
    return new_date

df['date'] = df['date'].apply(format_date_column)
start_events = ['διορισμος', 'αρχη_κυβερνησης']
end_events = ['παραιτηση', 'παυση', 'απεβιωσε', 'last_script_run',
              'τελος_κυβερνησης']


# CREATE FILE FOR COMPARISON WITH MANUAL ROLES
# match assignment and resignation dates for each role
print(df.columns)
for name, subdf in df.groupby(['cleaned_fullname','gov_date_from']):

    subdf = subdf.sort_values(by='date', ascending=True)#.reset_index(drop=True) #,inplace=True
    # if subdf.shape[0] != 2:
    #     print(subdf)
    #     print()

    for role in set(subdf.member_role.to_list()):

        role_subdf = subdf.loc[(subdf.member_role==role)]
        assignment_date = role_subdf.loc[(role_subdf.event.isin(start_events)),'date'].values[0]#.replace('-', '/')
        resignation_date = role_subdf.loc[(role_subdf.event.isin(end_events)),'date'].values[0]#.replace('-', '/')

        final_list.append([subdf.iloc[0].cleaned_fullname, role, assignment_date, resignation_date, subdf.iloc[0].gender])

    # merge_list = []
    # for index1, item_set1 in enumerate(final_list):
    #     for index2, item_set2 in enumerate(merge_list):
    #         print('2')
    #         items1 = item_set1.pop(2)
    #         items2 = item_set2.pop(2)
    #         print(items1)
    #         print(items2)
    #         if items1 == items2:
    #             merge_list[index2][2] = merge_list[index2][2]+', '+final_list[index1][2]
    #         else:
    #             print('1')
    # print(subdf)
    # break

# print(subdf)
final_df = pd.DataFrame(final_list, columns = ['member_name', 'role', 'role_start_date', 'role_end_date', 'gender'])
# print(final_df)

final_df.to_csv('../out_files/formatted_roles_gov_members_data.csv', encoding='utf-8',index=False)



# # CREATE FILE FOR MEMBER_SPEECH_MATCHER
#
# activity_entries = []
# # print(df.head())
# for name, subdf in df.groupby(['cleaned_fullname','gov_date_from']):
#     # print(subdf.iloc[0].cleaned_fullname)
#     # time.sleep(100)
#
#     out_ranges = []
#     subdf = subdf.sort_values(by='date', ascending=True)#.reset_index(drop=True) #,inplace=True
#     if subdf.shape[0] != 2: # which means more than one roles usually
#
#         date_pairs = [] # list of lists with paired dates
#
#         # merge overlapping time periods for the same roles
#         for role in set(subdf.member_role.to_list()):
#
#             role_subdf = subdf.loc[(subdf.member_role==role)]
#             assignment_date = role_subdf.loc[(role_subdf.event.isin(start_events)),'date'].values[0]#.replace('-', '/')
#             resignation_date = role_subdf.loc[(role_subdf.event.isin(end_events)),'date'].values[0]#.replace('-', '/')
#             date_pairs.append(([assignment_date, resignation_date]))
#
#         out_ranges = [date_pairs[0]]
#
#         for pair in date_pairs[1:]:
#
#             if out_ranges[-1][1] >= pair[0]:
#                 if out_ranges[-1][1] >= pair[1]: # end date is inside last range
#                     pass
#                 else:
#                     out_ranges[-1][1] = pair[1] # the current end date is outside last range
#
#             else: # current range does not overlap with last range at all
#                 out_ranges.append(pair)
#
#     else: # only one range available
#         out_ranges = [subdf.date.to_list()] # sorted date column to list
#
#     # if subdf.shape[0] != 2:
#     #     print('RESULT')
#     #     print(out_ranges)
#
#     for index, range1 in enumerate(out_ranges):
#         # print(range1)
#         # print(out_ranges)
#         activity_entries.append([subdf.iloc[0].cleaned_fullname,
#                                  #pd.to_datetime(
#                                   range1[0],
#                                  # ), pd.to_datetime(
#                                   range1[1]
#                                  # )
#                                  ,
#                                  #subdf.iloc[0].party, #not needed anymore
#                                  subdf.iloc[0].gender])
#
# activity_df = pd.DataFrame(data=activity_entries, columns = ['member_name', 'member_start_date', 'member_end_date', 'gender'])   # member_roles, gender
# activity_df.to_csv('../out_files/members_activity_1989onwards_with_gender_ggk_data.csv', encoding='utf-8', index=False) #index=False
# print(activity_df.columns)