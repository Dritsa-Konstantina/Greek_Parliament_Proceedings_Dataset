# -*- coding: utf-8 -*-
import re
from datetime import timedelta
import pandas as pd
import numpy as np

def party_formatting(party):
    if party=='ΑΝΕΞΑΡΤΗΤΟΙΕΛΛΗΝΕΣΕΘΝΙΚΗΠΑΤΡΙΩΤΙΚΗΔΗΜΟΚΡΑΤΙΚΗΣΥΜΜΑΧΙΑ':
        party='ανεξαρτητοι ελληνες εθνικη πατριωτικη δημοκρατικη συμμαχια'
    elif party=='ΑΝΕΞΑΡΤΗΤΟΙΕΛΛΗΝΕΣ-ΠΑΝΟΣΚΑΜΜΕΝΟΣ':
        party='ανεξαρτητοι ελληνες - πανος καμμενος'
    elif party=='ΑΝΕΞΑΡΤΗΤΟΙ':
        party= 'ανεξαρτητοι (εκτος κομματος)'
    elif party=='ΣΥΝΑΣΠΙΣΜΟΣ':
        party='συνασπισμος της αριστερας των κινηματων και της οικολογιας'
    elif party=='ΑΝΕΞΑΡΤΗΤΟΙΔΗΜΟΚΡΑΤΙΚΟΙΒΟΥΛΕΥΤΕΣ':
        party='ανεξαρτητοι δημοκρατικοι βουλευτες'
    elif party=='ΠΟΛ.Α.':
        party='πολιτικη ανοιξη'
    elif party=='ΟΟ.ΕΟ.':
        party='οικολογοι εναλλακτικοι (ομοσπονδια οικολογικων εναλλακτικων οργανωσεων)'
    elif party=='ΔΗ.ΑΝΑ.':
        party= 'δημοκρατικη ανανεωση'
    elif party=='ΔΗ.Κ.ΚΙ.':
        party='δημοκρατικο κοινωνικο κινημα'
    elif party=='ΕΝΩΣΗΚΕΝΤΡΩΩΝ':
        party='ενωση κεντρωων'
    elif party== 'ΝΕΑΔΗΜΟΚΡΑΤΙΑ':
        party='νεα δημοκρατια'
    elif party=='ΛΑ.Ο.Σ.':
        party= 'λαικος ορθοδοξος συναγερμος'
    elif party=='ΛΑΪΚΟΣΣΥΝΔΕΣΜΟΣ-ΧΡΥΣΗΑΥΓΗ':
        party='λαικος συνδεσος - χρυση αυγη'
    elif party=='ΚΟΜΜΟΥΝΙΣΤΙΚΟΚΟΜΜΑΕΛΛΑΔΑΣ':
        party='κομμουνιστικο κομμα ελλαδας'
    elif party=='Κ.Κ.Εσ':
        party='κομμουνιστικο κομμα ελλαδας εσωτερικου'
    elif party=='ΣΥΝΑΣΠΙΣΜΟΣΡΙΖΟΣΠΑΣΤΙΚΗΣΑΡΙΣΤΕΡΑΣ':
        party='συνασπισμος ριζοσπαστικης αριστερας'
    elif party=='ΛΑΪΚΗΕΝΟΤΗΤΑ':
        party='λαικη ενοτητα'
    elif party=='ΠΑ.ΣΟ.Κ.':
        party='πανελληνιο σοσιαλιστικο κινημα'
    elif party== 'ΔΗΜΟΚΡΑΤΙΚΗΑΡΙΣΤΕΡΑ':
        party='δημοκρατικη αριστερα'
    elif party=='ΔΗΜΟΚΡΑΤΙΚΗΣΥΜΠΑΡΑΤΑΞΗ(ΠΑΝΕΛΛΗΝΙΟΣΟΣΙΑΛΙΣΤΙΚΟΚΙΝΗΜΑ-ΔΗΜΟΚΡΑΤΙΚΗΑΡΙΣΤΕΡΑ)':
        party='δημοκρατικη συμπαραταξη (πανελληνιο σοσιαλιστικο κινημα - δημοκρατικη αριστερα)'
    elif party=='ΤΟΠΟΤΑΜΙ':
        party='το ποταμι'
    elif party=='ΕΝΩΣΗΚΕΝΤΡΟΥ-ΝΕΕΣΔΥΝΑΜΕΙΣΕΚ/ΝΔ':
        party='ενωση κεντρου - νεες δυναμεις (ε.κ. - ν.δ.)'
    elif party=='ΕΔΗΚ':
        party='ενωση δημοκρατικου κεντρου (εδηκ)'
    elif party=='ΕΘΝΙΚΗΠΑΡΑΤΑΞΙΣ':
        party='εθνική παράταξη'
    elif party=='ΕΘΝΙΚΗΠΑΡΑΤΑΞΙΣ':
        party='εθνικη παραταξη'
    elif party=='ΝΕΟΦΙΛΕΛΕΥΘΕΡΩΝ':
        party='κομμα νεοφιλελευθερων'
    elif party=='ΕΝΙΑΙΑΔΗΜΟΚΡΑΤΙΚΗΑΡΙΣΤΕΡΑ-Ε.Δ.Α.':
        party='ενιαια δημοκρατικη αριστερα (ε.δ.α.)'
    elif party=='ΣΥΜ/ΧΙΑΠΡ':
        party='συμμαχια προοδευτικων και αριστερων δυναμεων'
    elif party=='ΕΛΛΗΝΙΚΗΛΥΣΗ-ΚΥΡΙΑΚΟΣΒΕΛΟΠΟΥΛΟΣ':
        party='ελληνικη λυση - κυριακος βελοπουλος'
    elif party=='ΚΙΝΗΜΑΑΛΛΑΓΗΣ':
        party='κινημα αλλαγης'
    elif party=='ΜέΡΑ25':
        party='μετωπο ευρωπαικης ρεαλιστικης ανυπακοης (μερα25)'
    else:
        pass;
    return party

def name_formatting(name):

    name = re.sub(r"(\s*-\s*)|(\sή\s)",'-', name) #when people have two surnames or two names, we glue them together with '-' in the middle
    name = name.translate(str.maketrans('άΆέΈόΌώΏήΉίΊϊΐύΎϋΰ','αΑεΕοΟωΩηΗιΙιιυΥυυ'))
    name = re.sub(r"\t+" , " ", name)
    name = re.sub(r"΄", "", name)
    name = re.sub(r"\s\s+" , " ", name)
    name = re.sub(r"(συζ.\s)",'συζ.', name)
    name = re.sub("μαρια γλυκερια",'μαρια-γλυκερια', name)
    name = re.sub("χατζη χαβουζ γκαληπ",'χατζη-χαβουζ-γκαληπ', name)
    name = re.sub("μακρη θεοδωρου",'μακρη-θεοδωρου', name)
    name = re.sub("καρα γιουσουφ",'καρα-γιουσουφ', name)
    name = re.sub('χατζη οσμαν','χατζη-οσμαν', name)
    name = re.sub("σαδικ αμετ αμετ σαδηκ",'σαδικ αμετ αμετ', name)
    name = re.sub('ακριτα χα λουκη συλβα-καιτη','ακριτα συζ.λουκη συλβα-καιτη', name)
    name = re.sub('ιωανννης','ιωαννης', name)

    # specific correction missing father's name
    if name == 'βαγενα-κηλαηδονη αννα':
        name = 'βαγενα-κηλαηδονη γεωργιου αννα'
    if name == 'μονογυιου αικατερινη':
        name = 'μονογυιου χχχχχχχ αικατερινη'
    if name == 'ληναιος-μητυλιναιος γεωργιου (στεφανος)-διονυσιος':
        name = 'ληναιος-μητυληναιος γεωργιου στεφανος (διονυσιος)'
    if name == 'βεττα καλλιοπη':
        name = 'βεττα χχχχχχχ καλλιοπη'
    name = name.rstrip()
    return name

def region_formatting(region):
    region = (region.lower()).translate(str.maketrans('άέόώήίϊΐiύϋΰ','αεοωηιιιιυυυ'))
    region = re.sub(r"\t+" , " ", region)
    region = re.sub(r"΄", " ", region)
    region = re.sub(r"\s\s+" , " ", region)
    region = region.rstrip()
    if region=="α'θεσσαλονικης":
        region= "α' θεσσαλονικης"
    elif region=="α'αθηνων":
        region="α' αθηνων"
    elif region == "β'θεσσαλονικης":
        region = "β' θεσσαλονικης"
    elif region == "β'αθηνων":
        region = "β' αθηνων"
    elif region == "β2'δυτικουτομεααθηνων":
        region = "β2' δυτικου τομεα αθηνων"
    elif region == "α ανατολικησαττικης":
        region = "α' ανατολικης αττικης"
    elif region == "α'πειραιως":
        region = "α' πειραιως"
    elif region == "β'πειραιως":
        region = "β' πειραιως"
    elif region == "β3 νοτιουτομεααθηνων":
        region = "β3' νοτιου τομεα αθηνων"
    elif region == "β δυτικησαττικης":
        region = "β' δυτικης αττικης"
    elif region == "β1'βορειουτομεααθηνων":
        region = "β1' βορειου τομεα αθηνων"
    return region


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
f = open('../out_files/original_members_data.csv', 'r+', encoding='utf-8')

df = pd.read_csv(f, encoding='utf-8', sep=',', header=None)

#rename columns
df.columns = ['no', 'member_name', 'period_date_range', 'event_date',
         'administrative_region', 'political_party',  'event_description']

# remove lines that contain "NO DATA"
df = df[~df['period_date_range'].str.contains("NO DATA")]

# remove characters from period
df['period_date_range'] = df['period_date_range'].\
    str.replace(r"[a-zA-Zα-ωΑ-Ω΄':()]", '')

# split dates of period start & end and create new columns
dates = df['period_date_range'].str.split('-', n=1, expand=True)

df['period_start_date'] = dates[0]
df['period_start_date'] = pd.to_datetime(df['period_start_date'],
                                         format='%d/%m/%Y')
df['period_end_date'] = dates[1]
df['period_end_date'] = pd.to_datetime(df['period_end_date'],
                                         format='%d/%m/%Y')
# drop old column
df.drop(columns=['period_date_range'], inplace=True)

# keep periods that end from 1989 onwards
df = df[(df['period_end_date'].dt.year >= 1989)]

# replace not needed strings in data cells
df['member_name'] = df['member_name'].str.replace("Name:", '')
df['event_date'] = df['event_date'].str.replace("Date:", '')
df['administrative_region'] = df['administrative_region'].str.replace("Administrative-Region:", '')
df['event_date'] = pd.to_datetime(df['event_date'], format='%d/%m/%Y')
df['political_party'] = df['political_party'].str.replace(
    "Parliamentary-Party:", '')
df['event_description'] = df['event_description'].str.replace("Description:",'')

# Format political party information
df['political_party'] = df['political_party'].apply(party_formatting)

df['administrative_region'] = df['administrative_region'].apply(region_formatting)

new_dfrows_list = []

start_cases = ['aντικατέστησε',
               'εκλογής',
               ]

end_cases = ['παραίτησηςαπότοβουλευτικόαξίωμα',
             'απεβίωσε',
             'έκπτωσηςβουλευτικούαξιώματος',
             'δολοφονήθηκε',
             ]

change_party_cases = ['προσχώρησης/επανένταξης',
                      'προσχώρηση',
                      'ανεξαρτητοποίηση',
                      'προσχωρησηστηνκ.ο.τησνεασδημοκρατιας',
                      'ετέθηεκτός',
                      'διεγράφη',
                      ]
error_cases = []

# for each starting period of a parliament member
for id, subdf in df.groupby(['no','period_start_date']):


    # remove specific error in data for 'πλακιωτάκης ιωσήφ ιωάννης'
    if id==('No:1435', pd.Timestamp('2015-09-20 00:00:00')):
        subdf = subdf[subdf['event_date'] != pd.to_datetime('2019-07-07')]

    rows_num = subdf.shape[0]

    member_name = name_formatting((subdf.iloc[0]['member_name']).lower())
    end_follows = False #refers to change of political party or any of the end cases
    change_follows = False #refers to change of political party

    # one and only either εκλογης or αντικατεστησε
    if rows_num==1:

        if any((subdf.iloc[0]['event_description'].lower()).startswith(s) for s in start_cases):

            member_start_date = subdf.iloc[0]['event_date']
            member_end_date = subdf.iloc[0]['period_end_date']
            political_party = subdf.iloc[0]['political_party']
            administrative_region = subdf.iloc[0]['administrative_region']

            new_dfrows_list.append({'member_name': member_name,
                                    'member_start_date': member_start_date,
                                    'member_end_date': member_end_date,
                                    'political_party': political_party,
                                    'administrative_region': administrative_region,
                                    })
        else:
            print('Probably missing data of case '+str(id)+', '+
                  str(subdf.iloc[0]['member_name']))
            print()

    else:

        for i in range(rows_num-1,-1,-1):

            if any((subdf.iloc[i]['event_description'].lower()).startswith(e) for e in end_cases):

                member_end_date = subdf.iloc[i]['event_date']
                last_event_date = subdf.iloc[i]['event_date']
                last_political_party = subdf.iloc[i]['political_party']
                end_follows = True
                change_follows = False

            elif any(p in subdf.iloc[i]['event_description'].lower() for p in change_party_cases):

                if end_follows:
                    member_end_date = last_event_date
                elif change_follows:
                    member_end_date = last_event_date - timedelta(days=1)
                else:
                    member_end_date = subdf.iloc[i]['period_end_date']

                member_start_date = subdf.iloc[i]['event_date']
                political_party = subdf.iloc[i]['political_party']
                administrative_region = subdf.iloc[i]['administrative_region']

                new_dfrows_list.append({'member_name': member_name,
                                     'member_start_date': member_start_date,
                                     'member_end_date': member_end_date,
                                     'political_party': political_party,
                                    'administrative_region': administrative_region,
                                      })

                if end_follows:
                    if last_political_party != political_party:
                        # print('Error in data of case '+id)
                        error_cases.append(subdf.iloc[i]['event_description'].lower())
                        print(subdf.iloc[i]['no'].lower())

                #update last event
                last_event_date = subdf.iloc[i]['event_date']
                last_political_party = subdf.iloc[i]['political_party']
                end_follows = False
                change_follows = True

            elif any((subdf.iloc[i]['event_description'].lower()).startswith(s) for s in start_cases):
                member_start_date = subdf.iloc[i]['event_date']
                administrative_region = subdf.iloc[i]['administrative_region']


                if end_follows:
                    new_dfrows_list.append({'member_name': member_name,
                                          'member_start_date': member_start_date,
                                          'member_end_date': member_end_date,
                                          'political_party': last_political_party,
                                            'administrative_region': administrative_region,
                                          })
                elif change_follows:
                    member_end_date = last_event_date - timedelta(days=1)
                    political_party = subdf.iloc[i]['political_party']
                    new_dfrows_list.append({'member_name': member_name,
                                          'member_start_date': member_start_date,
                                          'member_end_date': member_end_date,
                                          'political_party': political_party,
                                            'administrative_region': administrative_region,
                                          })

                # if nothing follows like the case of Διαμαντίδης Δημήτριος
                else:
                    member_end_date = subdf.iloc[i]['period_end_date']
                    political_party = subdf.iloc[i]['political_party']
                    new_dfrows_list.append({'member_name': member_name,
                                          'member_start_date': member_start_date,
                                          'member_end_date': member_end_date,
                                          'political_party': political_party,
                                          'administrative_region': administrative_region,
                                          })

                    print('Check case for '+str(subdf.iloc[i]['member_name'])+
                          ' around date '+str(subdf.iloc[i]['period_end_date']))


new_df = pd.DataFrame(new_dfrows_list,
                      columns=['member_name', 'member_start_date',
                               'member_end_date', 'political_party',
                               'administrative_region',
                               ])

# drop activity that ends before 1/1/1989
new_df = new_df[(new_df['member_end_date'].dt.year >= 1989)]

# replace start dates before 1989 with 1/1/1989
new_df['member_start_date'] = np.where(new_df['member_start_date']<'1989-01-01',
                                       pd.to_datetime(['1989-01-01']),
                                       new_df['member_start_date'])

new_df.to_csv('../out_files/members_activity_1989onwards.csv', header=True,index=False, encoding='utf-8')