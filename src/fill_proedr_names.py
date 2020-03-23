import pandas as pd
import numpy as np

df = pd.read_csv('../out_files/tell_all.csv', encoding='utf-8')

# Columns needed for creating reference df_proedr
subdf = df[['member_name', 'sitting_date', 'parliamentary_sitting', 'speaker_info', 'member_gender']]

# Rows with only proedros and proedreuon speaker info, as search reference
df_proedr = subdf.loc[((subdf['speaker_info'] == 'προεδρευων') |
                       (subdf['speaker_info']=='προεδρος') |
                       (subdf['speaker_info']=='προσωρινος προεδρος')
                       )]

# Create df where each row has name(s) of proedreuon or proedros for specific date and sitting
df_grouped_proedr = df_proedr.groupby(['sitting_date', 'parliamentary_sitting',
                                       'speaker_info', 'member_gender']
                                      )['member_name'].apply(lambda x: ' / '.join(set(x.dropna()))).reset_index()

# fill emptied cells with NaN value
df_grouped_proedr = df_grouped_proedr.replace('', np.nan)

proedr_nan = 0

for index, row in df.iterrows():

    if pd.isnull(row['member_name']):

        if (row['speaker_info'] == 'προεδρευων'):

            proedr_nan += 1

            # get the respective row from reference dataframe df_grouped_proedr
            proedeuon_slice = df_grouped_proedr.loc[(df_grouped_proedr['sitting_date'] == row['sitting_date'])
                                                    & (df_grouped_proedr['parliamentary_sitting'] == row['parliamentary_sitting'])
                                                    & (df_grouped_proedr['speaker_info'] == 'προεδρευων')].reset_index()
            if not proedeuon_slice.empty:

                if not pd.isnull(proedeuon_slice['member_name'][0]):

                    # replace NaN with name, only if name is only one
                    if len(proedeuon_slice['member_name'][0].split('/')) == 1:
                        proedr_name = proedeuon_slice['member_name'][0] #row 0 column member_name
                        df.loc[index, 'member_name'] = proedr_name
                        df.loc[index, 'member_gender'] = proedeuon_slice['member_gender'][0]

        elif ((row['speaker_info'] == 'προεδρος') | (row['speaker_info'] == 'προσωρινος προεδρος')):

            proedr_nan += 1

            # get the respective row from reference dataframe df_grouped_proedr
            proedros_slice = df_grouped_proedr.loc[(df_grouped_proedr['sitting_date'] == row['sitting_date'])
                                                    & (df_grouped_proedr['parliamentary_sitting'] == row['parliamentary_sitting'])
                                                    & ((df_grouped_proedr['speaker_info'] == 'προεδρος') |
                                                       (df_grouped_proedr['speaker_info'] == 'προσωρινος προεδρος')
                                                       )].reset_index()

            if not proedros_slice.empty:

                if not pd.isnull(proedros_slice['member_name'][0]):

                    # replace NaN with name, only if name is only one
                    if len(proedros_slice['member_name'][0].split('/')) == 1:
                        proedr_name = proedros_slice['member_name'][0] #row 0 column member_name
                        df.loc[index, 'member_name'] = proedr_name
                        df.loc[index, 'member_gender'] = proedros_slice['member_gender'][0]


    if index%5000 == 0:
        print(index)

df.to_csv('../out_files/tell_all_filled.csv', index=False, na_rep=np.nan)

print('All NaN proedr cells are: ', str(proedr_nan))
print('Done')