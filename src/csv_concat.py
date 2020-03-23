# -*- coding: utf-8 -*-
import pandas as pd
import os

dir = '../tell_all_batches/'

with open('../out_files/tell_all.csv', 'w+', encoding='utf-8', newline = '') as outfile:

    for i,filepath in enumerate(sorted([os.path.join(os.path.abspath(dir), name)
                                 for name in os.listdir(dir)
                                 if not name.startswith('.')])):
        print(filepath)
        if i==0:
            combined_df = pd.read_csv(filepath, encoding='utf-8')
        else:
            combined_df = pd.concat([combined_df, pd.read_csv(filepath, encoding='utf-8')],
                                    ignore_index=True)

    combined_df.to_csv(outfile)

