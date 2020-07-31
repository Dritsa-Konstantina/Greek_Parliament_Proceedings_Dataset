# -*- coding: utf-8 -*-
import pandas as pd
import csv
import sys
import os
import numpy as np


dir = '../tell_all_batches/'


# for filename in os.listdir(dir):
#     if not filename.startswith('.'):
#         print(os.path.join(os.path.abspath(dir), filename))

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


    # combined_csv = pd.concat([pd.read_csv(f, encoding='utf-8', header=None)
    #                           for f in (os.listdir(tell_all_batches_path))
    #                                     if not f.startswith('.')])
    combined_df.to_csv(outfile) #, index=False,, header=False

# print(combined_df)
