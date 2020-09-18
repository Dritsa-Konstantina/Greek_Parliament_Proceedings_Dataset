import pandas as pd
import numpy as np

# Input file created by member_speech_matcher.py
df = pd.read_csv('../out_files/tell_all.csv', encoding='utf-8')

# Delete columns not needed for creating reference df_proedr
subdf = df.copy()
del subdf['speech']
del subdf['parliamentary_session']
del subdf['parliamentary_period']

# Choose rows with only proedros and proedreuon speaker info, as search reference
df_proedr = subdf.loc[((subdf['speaker_info'] == 'προεδρευων') |
                       (subdf['speaker_info'] == 'προεδρος') |
                       (subdf['speaker_info'] == 'προσωρινος προεδρος')
                       )]

''' Group df so that each row has name(s) of proedreuon or proedros for specific
    date and sitting joined with a ' / '
    note: in some cases multiple proedreuontes iterate within a long sitting'''
df_grouped_proedr = df_proedr.groupby(['sitting_date', 'parliamentary_sitting',
                                       'speaker_info', 'member_gender', 'government',
                                       'member_region', 'roles', 'political_party']
                                      )['member_name'].apply(lambda x: ' / '.join(set(x.dropna()))).reset_index()

# Fill emptied cells with NaN value
df_grouped_proedr = df_grouped_proedr.replace('', np.nan)


''' For each of the rows of the initial file that does not have a proedreuon or proedros name
    search in the new df of proedreuontes for the name and replace NaN with the actual name'''
proedr_nan = 0

for index, row in df.iterrows():

    # if row member name is NaN
    if pd.isnull(row['member_name']):

        if (row['speaker_info'] == 'προεδρευων'):

            proedr_nan += 1

            # Get the respective row from reference dataframe df_grouped_proedr
            proedeuon_slice = df_grouped_proedr.loc[(df_grouped_proedr['sitting_date'] == row['sitting_date'])
                                                    & (df_grouped_proedr['parliamentary_sitting'] == row['parliamentary_sitting'])
                                                    & (df_grouped_proedr['speaker_info'] == 'προεδρευων')].reset_index()

            if not proedeuon_slice.empty:
                if not pd.isnull(proedeuon_slice['member_name'][0]):

                    # Replace NaN with name, only if name is only one
                    if len(proedeuon_slice['member_name'][0].split('/')) == 1:
                        proedr_name = proedeuon_slice['member_name'][0] #row 0 column member_name
                        df.loc[index, 'member_name'] = proedr_name
                        df.loc[index, 'member_gender'] = proedeuon_slice['member_gender'][0]
                        df.loc[index, 'government'] = proedeuon_slice['government'][0]
                        df.loc[index, 'member_region'] = proedeuon_slice['member_region'][0]
                        df.loc[index, 'roles'] = proedeuon_slice['roles'][0]
                        df.loc[index, 'political_party'] = proedeuon_slice['political_party'][0]

        elif ((row['speaker_info'] == 'προεδρος') | (row['speaker_info'] == 'προσωρινος προεδρος')):

            proedr_nan += 1

            # Get the respective row from reference dataframe df_grouped_proedr
            proedros_slice = df_grouped_proedr.loc[(df_grouped_proedr['sitting_date'] == row['sitting_date'])
                                                    & (df_grouped_proedr['parliamentary_sitting'] == row['parliamentary_sitting'])
                                                    & ((df_grouped_proedr['speaker_info'] == 'προεδρος') |
                                                       (df_grouped_proedr['speaker_info'] == 'προσωρινος προεδρος')
                                                       )].reset_index()

            if not proedros_slice.empty:

                if not pd.isnull(proedros_slice['member_name'][0]):

                    # Replace NaN with name, only if name is only one
                    if len(proedros_slice['member_name'][0].split('/')) == 1:
                        proedr_name = proedros_slice['member_name'][0] #row 0 column member_name
                        df.loc[index, 'member_name'] = proedr_name
                        df.loc[index, 'member_gender'] = proedros_slice['member_gender'][0]
                        df.loc[index, 'government'] = proedros_slice['government'][0]
                        df.loc[index, 'member_region'] = proedros_slice['member_region'][0]
                        df.loc[index, 'roles'] = proedros_slice['roles'][0]
                        df.loc[index, 'political_party'] = proedros_slice['political_party'][0]

    if index%5000 == 0:
        print(index)

df.to_csv('../out_files/tell_all_FILLED.csv', index=False, na_rep=np.nan)

print('All NaN proedr cells are: ', str(proedr_nan))
print('Done')
