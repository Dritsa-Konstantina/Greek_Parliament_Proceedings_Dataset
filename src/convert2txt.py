# -*- coding: utf-8 -*-
import os
import subprocess
import re
import shutil
from tools import greek_numerals_to_numbers
from datetime import datetime as dt
import time

datapath = "../original_data/"
new_datapath = "../_data/"

# ignore hidden files
filenames = [f for f in os.listdir(datapath) if not f.startswith('.')]

#Keep history of changes
renaming_log = open('../out_files/renaming_log.txt','wb')

counter=0

for filename in filenames:

    #If filesize is zero, delete the file and do not copy it
    if os.path.getsize(datapath+filename) == 0:
        renaming_log.write(
            b'0 size file : ' + filename.encode("utf-8") + b'\n\n')

        os.remove(datapath+filename)


    #If filesize is not zero, rename, copy and convert it to text
    else:

        file_date = filename.split('_')[0]

        file_datetime_object = dt.strptime(file_date, '%Y-%m-%d')

        counter+=1
        print('File No. ', counter)

        segments = (re.sub("[΄'`’]", "'", os.path.splitext(filename)[0])).split('_') #segments of filename seperated with underscore
        part1 = '_'.join(segments[:2]) #Date and counter number

        #PERIOD

        period = segments[2]

        if period!='':
            period = re.sub(r'[\(-\)-]', '', period) #remove parentheses and dashes

            if "θ'περιοδος" in period:
                period = period.replace("θ'","θ' ")

            if 'προεδρευομενης κοινοβουλευτικης δημοκρατιας' in period:
                period = period.replace('προεδρευομενης κοινοβουλευτικης δημοκρατιας', 'presided-parliamentary-republic')

            period = period.split(' ')
            period_number = greek_numerals_to_numbers(period[0])

            if 'αναθεωρητική' in period:
                review_number = greek_numerals_to_numbers(period[2])
                new_period = 'period-'+period_number+'-review-'+review_number+'-'.join(period[4:])
            else:
                new_period = 'period-'+period_number+'-'+'-'.join(period[2:])

        else:
            new_period = ''

        #SESSION

        session = segments[3]

        if session!='':
            session = session.replace("γ'τμήμα", "γ' τμήμα")

            section = session.split(' ')
            if "'" in section[0]:
                session_number = greek_numerals_to_numbers(section[0])

            if (re.search(r'\d', section[-1])):
                year = re.sub("[()]", '', section[-1])

            if 'τμήμα διακοπής εργασιών βουλής θέρους' in session:
                new_session = year+'-summer-recess-section-'+session_number
            elif 'θέρο' in session:
                session = session.replace('θέρος', 'summer')
                session = session.replace('συνέχιση θέρους', 'continuation-of-summer-recess')
                new_session = session.replace(' ', '-')
            elif 'έκτακτη σύνοδος' in session:
                new_session = session.replace('έκτακτη σύνοδος', 'parliament-recall-extraordinary-session')
            elif 'συνέχιση ολομέλειας' in session:
                new_session = 'session-'+session_number+'-(continuation-of-plenary-session)'
            else:
                new_session = 'session'+'-'+session_number
        else:
            new_session = ''

        #SITTING

        sitting = segments[4]

        if sitting!='':
            if sitting=='ειδικη συνεδριαση ημερα της γυναικας':
                new_sitting = "special-sitting-international-women-'s-day"
            elif sitting=='ειδικη ημερησια διαταξη της ολομελειας της βουλης':
                 new_sitting = 'a-special-agenda-for-the-plenary-session-of-the-parliament'
            elif sitting=='ειδικη εκδηλωση για την επετειο της γενοκτονιας των ποντιων στη βουλη':
                new_sitting = 'special-event-anniversary-of-Pontic-Greek-genocide'
            elif sitting=='βουλη των εφηβων':
                new_sitting = 'Youth-Parliament'
            else:
                sitting_number = greek_numerals_to_numbers(sitting)
                new_sitting = 'sitting-'+sitting_number
        else:
            new_sitting = ''

        ext = os.path.splitext(filename)[1] #initial file extension including dot

        #Compose new name without extension
        new_filename = part1+'_'+new_period+'_'+new_session+'_'+new_sitting+ext

        shutil.copy(datapath+filename,new_datapath+new_filename)#copy and rename file to new location

        if ext.lower()!='.txt':
            command = 'java -jar tika-app-1.20.jar --text --encoding=utf-8 '+new_datapath+new_filename+'>'+new_datapath+os.path.splitext(new_filename)[0]+'.txt'
            print(command)
            time.sleep(5)
            subprocess.call(command, shell=True) #shell=True hides console window
#            os.system(command)
            os.remove(new_datapath+new_filename) #delete initial non-txt files and keep only converted files

        renaming_log.write(b'Before: '+filename.encode("utf-8")+b'\nAfter: '+(os.path.splitext(new_filename)[0]+'.txt').encode("utf-8")+b'\n\n')

renaming_log.close()