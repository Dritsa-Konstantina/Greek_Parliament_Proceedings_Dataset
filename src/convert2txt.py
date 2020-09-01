# -*- coding: utf-8 -*-
import os
import subprocess
import re
import shutil
from datetime import datetime as dt

def greek_numerals_to_numbers(numeral):

    number = 0

    greek_numerals = {"α": 1,"a":1, "β": 2, "b":2, "γ": 3,"δ": 4, "ε": 5, "έ":5, "e":5,
                      "στ": 6, "ζ": 7, "z":7,"η": 8, "ή":8, "h":8, "θ": 9,
                      "ι": 10, "i":10, "κ": 20, "k":20, "λ": 30, "μ": 40,
                      "m":40, "ν": 50, "n":50, "ξ": 60,"ο": 70, "o":70, "ό":70,
                      "π": 80, "ϙ": 90, "ϟ":90, "ρ": 100,"p":100, "σ": 200, "τ": 300,
                      "t":300, "υ": 400, "φ": 500, "χ": 600,"ψ": 700, "ω": 800,
                      "ϡ": 900}

    numeral = re.sub("[΄'`’(); r'\d']","", numeral)

    numeral_letters = list(numeral.lower())

    new_letters=[]

    for i in range(len(numeral_letters)):
        if numeral_letters[i] == 'σ':
            if i!=len(numeral_letters)-1: #if σ is not the last letter
                if numeral_letters[i+1]== 'τ': #if σ is followed by τ
                    new_letters.append('στ') #join σ and τ
            else:
                new_letters.append(numeral_letters[i])
        elif numeral_letters[i] == 'τ':
            pass
        else:
            new_letters.append(numeral_letters[i])

    for letter in new_letters:
        number+= greek_numerals[letter]

    return str(number)


datapath = "../original_data/"
new_datapath = "../_data/"
if not os.path.exists(new_datapath):
    os.makedirs(new_datapath)

# ignore hidden files
filenames = [f for f in os.listdir(datapath) if not f.startswith('.')]

#Keep history of changes
with open('../out_files/renaming_log.txt', 'wb') as renaming_log:

    counter=0

    for filename in filenames:

        #If filesize is zero, delete the file and do not copy it
        if os.path.getsize(datapath+filename) == 0:
            renaming_log.write(
                b'0 size file : ' + filename.encode("utf-8") + b'\n\n')

            os.remove(os.path.join(datapath, filename))
            print('Filesize is zero. File removed.\n')


        #If filesize is not zero, rename, copy and convert it to text
        else:

            file_date = filename.split('_')[0]

            file_datetime_object = dt.strptime(file_date, '%Y-%m-%d')

            counter += 1
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

            # copy and rename file to new location
            shutil.copy(os.path.join(datapath, filename),
                        os.path.join(new_datapath, new_filename))

            if ext.lower()!='.txt':
                command = 'java -jar tika-app-1.20.jar --text --encoding=utf-8 '+os.path.join(new_datapath, new_filename)\
                          +'>'+os.path.join(new_datapath, os.path.splitext(new_filename)[0])+'.txt'

                print(command)
                subprocess.call(command, shell=True) #shell=True hides console window

                # delete initial non-txt files and keep only converted files
                os.remove(os.path.join(new_datapath, new_filename))
            else:
                print('File already in txt format.\n')

            renaming_log.write(b'Before: '+filename.encode("utf-8")+b'\nAfter: '+(os.path.splitext(new_filename)[0]+'.txt').encode("utf-8")+b'\n\n')