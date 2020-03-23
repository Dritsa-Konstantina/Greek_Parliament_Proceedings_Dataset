import re
import pandas as pd

with open('../out_files/female_names_alternatives_gr.txt', 'r+', encoding = 'utf-8') as f1,\
     open('../out_files/male_names_alternatives_gr.txt', 'r+', encoding = 'utf-8') as f2:

    female_list = re.split(r'[,\n\s*]', f1.read())
    male_list = re.split(r'[,\n\s*]', f2.read())

    male_list.extend(['διακος', 'τσετιν', 'σπυροπανος', 'σπυριδωνας', 'τερενς',
                     'αιχαν', 'χουσειν', 'πυρρος', 'γκαληπ', 'μπηρολ', 'φιντιας',
                     'τραιανος', 'αχμετ', 'αθηναιος', 'φρανς', 'τζαννης',
                     'ροβερτος', 'μουσταφα', 'κλεων', 'παρισης', 'παυσανιας',
                      'μεχμετ', 'αμετ', 'μπουρχαν', 'πανουργιας', 'γιανης',
                      'ιλχαν', 'πυθαγορας', 'φραγκλινος', 'ισμαηλ', 'θαλασσινος'])

    female_list.extend(['ελεωνορα', 'κρινιω', 'ιωαννετα', 'σουλτανα', 'ηρω',
                       'συλβα', 'χρυσουλα', 'ελισσαβετ', 'βιργινια', 'ροδουλα',
                        'καλλιοπη', 'γεσθημανη', 'φερονικη', 'χρυση', 'ολυμπια',
                        'καλλιοπη'])

    # remove empty strings
    female_list = list(filter(None, female_list))
    male_list = list(filter(None, male_list))

    #keep names used for both males and females
    unisex_names = list(set(male_list).intersection(female_list))

    df = pd.read_csv('../out_files/members_activity_1989onwards.csv')

    df['gender']=''

    for index, row in df.iterrows():

        first_name = (row['member_name'].split(' ')[2]).lower()
        if '-' in first_name:
            first_name = first_name.split('-')[0]

        if first_name in unisex_names:
            print('check manually case of ', row['member_name', '. The name is unisex.'])
        elif first_name in female_list:
            row['gender'] = 'female'
        elif first_name in male_list:
            row['gender'] = 'male'
        else:
            print('Name not categorized in any gender: ',row['member_name'])


df.to_csv('../out_files/members_activity_1989onwards_with_gender.csv', header=True, index=False, encoding='utf-8')
