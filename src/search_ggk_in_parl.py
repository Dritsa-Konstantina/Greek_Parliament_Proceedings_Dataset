import pandas as pd
from collections import Counter, defaultdict
import re
import time
import numpy as np
pd.set_option('display.max_columns', None)

def remove_father_name(name):
    name_parts = name.split(' ')
    new_name = name_parts[0]+' '+ ' '.join(name_parts[2:])
    return new_name

def gov_name_formatting(df):

    d = {r'\bαντωνης\b': 'αντωνιος',
         r'\bαχιλλευς\b': 'αχιλλεας',
         r'\bγιωργος\b': 'γεωργιος',
         r'\bγιαννης\b': 'ιωαννης',
         }
    # regex False exact full string match,
    # regex True substrings replaced unless use \bstring\b in first parenthesis. regex only in first parenthesis
    df['member_name_copy'] = df['member_name'].copy().replace(d, regex=True)

    return(df)

def ggk_name_formatting(df):

    d = {r'\bβυρωνας\b': 'βυρων',
         r'\bεμμανουηλ λουκακης\b': 'μανωλης λουκακης',
         r'\bκιμωνας κουλουρης\b': 'κιμων κουλουρης',
         r'\bκωνσταντινος σημιτης\b': 'κωστας σημιτης',
         r'\bμιχαηλ παπαδοπουλος\b': 'μιχαλης παπαδοπουλος',
         r'\bμιχαηλ παπακωνσταντινου\b': 'μιχαλης παπακωνσταντινου',
         r'\bμιχαηλ-γεωργιος λιαπης\b': 'μιχαλης γεωργιος λιαπης',
         r'\bνικολαος χριστοδουλακης\b': 'νικος χριστοδουλακης'
         }
    # regex False exact full string match,
    # regex True substrings replaced unless use \bstring\b in first parenthesis. regex only in first parenthesis
    df['member_name'] = df['member_name'].replace(d, regex=True)

    return(df)

def add_government_column(df, df_govs):

    # Convert to datetime type for best date comparisons
    df['government_name'] = [[] for _ in range(df.shape[0])]
    df['member_start_date'] = pd.to_datetime(df['member_start_date'])
    df['member_end_date'] = pd.to_datetime(df['member_end_date'])
    df_govs['date_from'] = pd.to_datetime(df_govs['date_from'])#.dt.date
    df_govs['date_to'] = pd.to_datetime(df_govs['date_to'])#.dt.date
    df_govs = df_govs.sort_values(by='date_from', ascending=True)

    # drop rows before first government
    mask = (df['member_end_date'] >= df_govs.at[0,'date_from']) #'1989-07-03'
    df = df.loc[mask]

    # print((df_govs.date_from[0]))
    # print(df_govs.columns)
    # print(df.columns)
    # print(':')

    for index1, row1 in df.iterrows():
        matched_to_government = False
        for index2, row2 in df_govs.iterrows():
            try:
                if (row1.member_start_date>=row2.date_from and
                    row1.member_start_date<row2.date_to #< and not <= because last gov date is given to next gov
                    ) or (
                    row1.member_end_date>=row2.date_from and
                    row1.member_end_date<row2.date_to #< and not <= because last gov date is given to next gov
                    ) or (
                    row1.member_start_date<=row2.date_from and
                    row1.member_end_date>=row2.date_to):

                    item = row2['gov_name']+'('+str(row2.date_from.strftime('%d/%m/%Y'))+'-'+\
                           str(row2.date_to.strftime('%d/%m/%Y'))+')'
                    df.at[index1,'government_name'].append(item)
                    matched_to_government = True
            except:
                print('PROBLEM: cannot compare government dates and member dates')
                print(row1.member_start_date, type(row1.member_start_date))
                print(row2.date_from, type(row2.date_from))

        if matched_to_government == False:
            print('PROBLEM: not matched to existing government')
            print(row1)

    return(df)

# FILE 1
df_gov = pd.read_csv('../out_files/members_activity_1989onwards_with_gender.csv', encoding='utf-8')
#['member_name', 'member_start_date', 'member_end_date', 'political_party', 'administrative_region', 'gender']
df_gov = gov_name_formatting(df_gov) # add name copy column and proceed to adjustments
df_gov['member_name_copy'] = df_gov['member_name_copy'].apply(remove_father_name)
df_gov['roles'] = [[] for _ in range(df_gov.shape[0])]

# FILE 2
df_ggk= pd.read_csv('../out_files/formatted_roles_ggk_data.csv', encoding='utf-8')
# ['member_name', 'roles', 'gender']
df_ggk = ggk_name_formatting(df_ggk)

# FILE 3
df_extra = pd.read_csv('../out_files/extra_roles_manually.csv', encoding='utf-8')
df_extra['member_name'] = df_extra['member_name'].apply(remove_father_name)

df_roles = pd.concat([df_ggk, df_extra])

members_to_match = list(set(df_roles['member_name'].to_list())) # unique member names

# # Match members from df_roles to df_gov BY NAME AND DATES and find extra parliamentary members
df_roles['role_start_date'] = pd.to_datetime(df_roles['role_start_date']).dt.date
df_roles['role_end_date'] = pd.to_datetime(df_roles['role_end_date']).dt.date
df_gov['member_start_date'] = pd.to_datetime(df_gov['member_start_date']).dt.date
df_gov['member_end_date'] = pd.to_datetime(df_gov['member_end_date']).dt.date

extra_parliamentary = []

c=0

# Find the names in df_roles in the df_gov, in order to match and transfer roles
for index_ggk, row_ggk in df_roles.iterrows():

    c+=1
    if c%100==0:
        print(c)

    ggk_matched_to_gov = False
    ggk_name = row_ggk['member_name']
    ggk_name = re.sub(r'[-()]', ' ', ggk_name) # replace -()
    ggk_name = re.sub(r'\s\s+', ' ', ggk_name)
    ggk_parts = [i for i in ggk_name.split(' ') if i != '']

    # if we find a match, we don't break. continue iteration because it might
    # match to more than one periods as formed in the gov files
    for index_gov, row_gov in df_gov.iterrows():
        gov_name = row_gov['member_name_copy']
        gov_name = re.sub(r'[-()]', ' ', gov_name)  # replace -()
        gov_name = re.sub(r'\s\s+', ' ', gov_name)
        gov_parts = [i for i in gov_name.split(' ') if i!='']

        check = all(item in gov_parts for item in ggk_parts) #ggk_parts all in gov_parts

        # matched names
        if check:
            m_s = row_gov['member_start_date']
            m_e = row_gov['member_end_date']
            r_s = row_ggk['role_start_date']
            r_e = row_ggk['role_end_date']

            # if any date of active role is in the member activity range
            # if role start in member activity, or role end in member activity or activity in role of large range
            if (r_s>=m_s and r_s<=m_e) or (r_e>=m_s and r_e<=m_e) or (r_s<=m_s and r_e>=m_e):
                ggk_matched_to_gov = True
                item = row_ggk['role']+'('+str(row_ggk['role_start_date'].strftime('%d/%m/%Y')
                                               )+'-'+str(row_ggk['role_end_date'].strftime('%d/%m/%Y'))+')'
                df_gov.at[index_gov, 'roles'].append(item)

    # if df_roles name not in df_gov, it refers to extra parliamentary member
    if ggk_matched_to_gov == False:
        role_item = row_ggk['role']+'('+str(row_ggk['role_start_date'].strftime('%d/%m/%Y')
                                               )+'-'+str(row_ggk['role_end_date'].strftime('%d/%m/%Y'))+')'

        extra_parliamentary.append([row_ggk['member_name'], row_ggk['role_start_date']#.strftime('%d/%m/%Y'),
                                    , row_ggk['role_end_date']#.strftime('%d/%m/%Y'),
                                    , 'εξωκοινοβουλευτικός',np.nan, row_ggk['gender'], [role_item]])
    # if c==200:
    #     break

#['member_name', 'member_start_date', 'member_end_date',
#'political_party', 'administrative_region', 'gender', 'member_name_copy']
del df_gov['member_name_copy']

df_gov = df_gov.append(pd.DataFrame(data=extra_parliamentary, columns=df_gov.columns),
                       ignore_index=True)

df_govs = pd.read_csv('../out_files/governments_1989onwards.csv', encoding='utf-8')
df_gov = add_government_column(df_gov, df_govs)

df_gov.to_csv('../out_files/all_members_activity.csv', encoding='utf-8', index=False)

