# -*- coding: utf-8 -*-
import os
import re
import jellyfish
from collections import defaultdict
import csv
import numpy as np
from datetime import datetime as dt
from argparse import ArgumentParser
import pandas as pd
import ast


'''This script extracts speeches from record files and matches them to the
official parliament or government member from the file all_members_activity.csv.
The script takes as arguments from the command line
1) The path of the folder with the record files
2) The path to the folder where it outputs the speeches and the corresponding speakers
Example: python member_speech_matcher.py -f '../path/to/data/folder/' -o '../output/folder/tell_all.csv'
'''


starttime = dt.now()


#Cleaning and formatting speakers data
def text_formatting(text):
    text = re.sub("[():'’`΄‘]",' ', text)
    text = re.sub('\t+' , ' ', text) #replace one or more tabs with one space
    text = text.lstrip() #remove leading spaces
    text = text.rstrip() #remove trailing spaces
    text = re.sub('\s\s+' , ' ', text) #replace more than one spaces with one space
    text = re.sub('\s*(-|–)\s*' , '-', text) #fix dashes
    text = text.lower()
    text = text.translate(str.maketrans('άέόώήίϊΐiύϋΰ','αεοωηιιιιυυυ')) #remove accents
    text = text.translate(str.maketrans('akebyolruxtvhmnz','ακεβυολρυχτνημνζ')) #convert english chars to greek
    return text


def speaker_name_corrections(name):
    if 'γενηματα' in name:
        name = name.replace('γενηματα', 'γεννηματα')
    if 'βαρουφακης' in name:
        name = name.replace('γιαννης', 'γιανης')
    if 'ζουραρις' in name:
        name = name.replace('ζουραρις','ζουραρης')
    return name


# for example ΠΟΛΛΟΙ ΒΟΥΛΕΥΤΕΣ (από την πτέρυγα του ΠΑ.ΣΟ.Κ.):...
def party_of_generic_reference(speaker):

    if 'πασοκ' in speaker:
        party = 'πανελληνιο σοσιαλιστικο κινημα'
    elif 'δημοκρατια' in speaker:
        party = 'νεα δημοκρατια'
    elif'συνασπισμου' in speaker:
        party = 'συνασπισμος της αριστερας των κινηματων και της οικολογιας'
    elif 'λαος' in speaker:
        party = 'λαικος ορθοδοξος συναγερμος'
    elif 'συριζα' in speaker:
        party = 'συνασπισμος ριζοσπαστικης αριστερας'
    elif 'αντιπολιτευσ' in speaker:
        party = 'αντιπολιτευση'
    else:
        party = 'βουλη'
    return party


#For example ΦΩΤΕΙΝΗ (ΦΩΦΗ ΓΕΝΝΗΜΑΤΑ (Πρόεδρος της Δημοκρατικής Συμπαράταξης ΠΑΣΟΚ - ΔΗΜΑΡ):,2017
def separate_nickname_incomplete_parenthesis(speaker, speaker_nickname):
    lefts = 0
    rights = 0
    if left_parenthesis_regex.search(speaker):
        lefts = len(re.findall(left_parenthesis_regex, speaker))
    if right_parenthesis_regex.search(speaker):
        rights = len(re.findall(right_parenthesis_regex, speaker))
    if (lefts-rights) > 0:
        if incomplete_nickname_parenthesis.search(speaker):
            # Keep separately the nickname of the speaker
            speaker_nickname = (incomplete_nickname_parenthesis.search(speaker)).group()
            speaker_nickname = text_formatting(speaker_nickname)
            speaker = re.sub(incomplete_nickname_parenthesis, '', speaker) #remove nickname
    return speaker, speaker_nickname


# Keep separately the nickname of the speaker
def separate_nickname(speaker):
    speaker_nickname = (caps_nickname_in_parenthesis.search(speaker)).group()
    speaker_nickname = text_formatting(speaker_nickname)
    speaker = re.sub(caps_nickname_in_parenthesis, '', speaker) #remove nickname
    return speaker, speaker_nickname


# Keep separately the explanatory parenthesis text of the speaker
def separate_explanatory_parenthesis(speaker):
    speaker_info = (text_in_parenthesis.search(speaker)).group()
    speaker = re.sub(text_in_parenthesis, '', speaker) #remove (text in parenthesis)
    return speaker, speaker_info


def format_speaker_info(speaker_info):
    speaker_info = text_formatting(speaker_info)
    speaker_info = speaker_info.replace('υφυπ.',' υφυπουργος ')
    speaker_info = speaker_info.replace('υπ.',' υπουργος ')
    speaker_info = speaker_info.replace('&',' και ')
    speaker_info = re.sub('\s\s+' , ' ', speaker_info) #replace more than one spaces with one space
    speaker_info = speaker_info.lstrip() #remove leading spaces
    speaker_info = speaker_info.rstrip() #remove trailing spaces
    return speaker_info


# compare temp max with similarity of the member's name alternatives with the speaker name
def compare_with_alternative_sim(speaker_name, member_name, member_surname, temp_max, greek_names):

    # each row in the greek_names data is unique concerning the first name of the row
    # greek_names has only those names that have at least one alternative. so each line has at least two names
    for line in greek_names:

        name_list = (line.strip()).split(',')

        # if member name has alternatives
        if name_list[0]==member_name:

            # keep alternatives of the name
            name_list.remove(member_name)

            for alternative_name in name_list:
                alternative_sim1 = jellyfish.jaro_winkler_similarity(speaker_name, alternative_name+' '+member_surname)
                alternative_sim2 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname + ' ' + alternative_name)
                temp_max = max(temp_max,alternative_sim1, alternative_sim2)

            break #if true, break the for loop and proceed to return temp pax

    return temp_max


def get_gov(current_record_datetime):

    df_govs = pd.read_csv('../out_files/governments_1989onwards.csv', encoding='utf-8')
    df_govs['date_from'] = pd.to_datetime(df_govs['date_from'])#.dt.date
    df_govs['date_to'] = pd.to_datetime(df_govs['date_to'])#.dt.date
    df_govs = df_govs.sort_values(by='date_from', ascending=True)
    current_gov_df = df_govs.loc[(df_govs.date_from <= current_record_datetime) & (current_record_datetime < df_govs.date_to)]

    if current_gov_df.shape[0] != 1:
        print('problem with ', current_record_datetime)

    item = current_gov_df.gov_name.iloc[0] + '(' + current_gov_df.date_from.iloc[0].strftime('%d/%m/%Y') +\
           '-' + current_gov_df.date_to.iloc[0].strftime('%d/%m/%Y') + ')'

    return [item]


def keep_roles_at_date(roles, current_record_datetime):

    new_roles = []

    #assert type list
    if type(roles) != list:
        roles = ast.literal_eval(roles)

    for role in roles:
        role_name, role_dates = role.split('(')
        role_start_date, role_end_date = role_dates.replace(')', '').split('-')
        role_start_date = dt.strptime(role_start_date, '%d/%m/%Y')
        role_end_date = dt.strptime(role_end_date, '%d/%m/%Y')
        if role_start_date<=current_record_datetime<=role_end_date:
            new_roles.append(role)

    #if empty list
    if not new_roles:
        new_roles.append('βουλευτης')

    return new_roles


def compute_max_similarity(speaker_name, speaker_nickname, member_name_part):

    if ( '(' in member_name_part and len(member_name_part.split(' '))>3 ) or ( '(' not in member_name_part and len(member_name_part.split(' '))>2):
        member_surname = member_name_part.split(' ')[0]
        member_name = member_name_part.split(' ')[2]
    else: # εξωκοινοβουλευτικος χωρις ονομα πατρος
        member_surname = member_name_part.split(' ')[1]
        member_name = member_name_part.split(' ')[0]

    temp_max = 0

    # put these transpositions in the beginning, before we remove '-'
    # If member has more than one first names
    if '-' in member_name:
        # there are cases like member name being δενδιας νικολαος-γεωργιος
        # and detected speaker being ΝΙΚΟΛΑΟΣ ΔΕΝΔΙΑΣ

        # if member has two first names
        if len(member_name.split('-'))==2:
            member_name1, member_name2 = member_name.split('-')

        # if member has three first names
        elif len(member_name.split('-'))==3:
            member_name1, member_name2, member_name3 = member_name.split('-')

        # if member has more than one first names and one surname
        if '-' not in member_surname:
            # do the following for two first names
            sim5 = jellyfish.jaro_winkler_similarity(speaker_name, member_name1 + ' '+member_surname)
            sim6 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname+' '+member_name1)
            sim7 = jellyfish.jaro_winkler_similarity(speaker_name, member_name2 + ' '+member_surname)
            sim8 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname+' '+member_name2)

            temp_max = max(temp_max, sim5, sim6, sim7, sim8)
            # Extra comparisons for alternative names of members
            temp_max = compare_with_alternative_sim(speaker_name, member_name1, member_surname, temp_max, greek_names)
            temp_max = compare_with_alternative_sim(speaker_name, member_name2, member_surname, temp_max, greek_names)


            # do the following extra for three first names
            # for example κουικ φιλιππου τερενς-σπενσερ-νικολαος
            if len(member_name.split('-'))==3:
                sim9 = jellyfish.jaro_winkler_similarity(speaker_name, member_name3 + ' '+member_surname)
                sim10 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname + ' '+member_name3)
                temp_max = max(temp_max, sim9, sim10)
                # Extra comparisons for alternative names of members
                temp_max = compare_with_alternative_sim(speaker_name, member_name3,
                                                        member_surname, temp_max,
                                                        greek_names)

        else:
            # If member has more than one first names and two surnames, compare each one separately
            member_surname1,member_surname2=member_surname.split('-')
            sim5 = jellyfish.jaro_winkler_similarity(speaker_name, member_name1 + ' '+member_surname1)
            sim6 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname1+' '+member_name1)
            sim7 = jellyfish.jaro_winkler_similarity(speaker_name, member_name1+' '+member_surname2)
            sim8 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname2+' '+member_name1)
            sim9 = jellyfish.jaro_winkler_similarity(speaker_name, member_name2+' '+member_surname1)
            sim10 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname1+' '+member_name2)
            sim11 = jellyfish.jaro_winkler_similarity(speaker_name, member_name2+' '+member_surname2)
            sim12 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname2+' '+member_name2)

            temp_max = max(temp_max, sim5, sim6, sim7, sim8, sim9, sim10, sim11, sim12)
            #there is no case with 3 first names and 2 last names, so we don't compute that

            # Extra comparisons for alternative names of members
            temp_max = compare_with_alternative_sim(speaker_name, member_name1, member_surname1, temp_max, greek_names)
            temp_max = compare_with_alternative_sim(speaker_name, member_name1, member_surname2, temp_max, greek_names)
            temp_max = compare_with_alternative_sim(speaker_name, member_name2, member_surname1, temp_max, greek_names)
            temp_max = compare_with_alternative_sim(speaker_name, member_name2, member_surname2, temp_max, greek_names)

    # If member has one first name and two surnames
    elif '-' in member_surname:
        member_surname1,member_surname2=member_surname.split('-')
        sim5 = jellyfish.jaro_winkler_similarity(speaker_name, member_name+' '+member_surname1)
        sim6 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname1+' '+member_name)
        sim7 = jellyfish.jaro_winkler_similarity(speaker_name, member_name+' '+member_surname2)
        sim8 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname2+' '+member_name)

        temp_max = max(temp_max, sim5, sim6, sim7, sim8)

        # Extra comparisons for alternative names of members
        temp_max = compare_with_alternative_sim(speaker_name, member_name, member_surname1, temp_max, greek_names)
        temp_max = compare_with_alternative_sim(speaker_name, member_name, member_surname2, temp_max, greek_names)

        #If member has available nickname and two surnames
        if lower_nickname_in_parenthesis.search(member_name_part) and speaker_nickname=='':

            member_nickname = re.sub ('[()]','',(lower_nickname_in_parenthesis.search(member_name_part)).group())
            sim9 = jellyfish.jaro_winkler_similarity(speaker_name, member_nickname+' '+member_surname1)
            sim10 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname1+' '+member_nickname)
            sim11 = jellyfish.jaro_winkler_similarity(speaker_name, member_nickname+' '+member_surname2)
            sim12 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname2+' '+member_nickname)

            temp_max = max(temp_max, sim9, sim10, sim11, sim12)

    # Remove '-' for sim1, sim2 best comparisons
    member_name = member_name.replace('-', ' ')
    member_surname = member_surname.replace('-', ' ')

    #Make comparisons of speaker with members' names and reversed members' names
    sim1 = jellyfish.jaro_winkler_similarity(speaker_name, member_name+' '+member_surname)
    sim2 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname+' '+member_name)
    temp_max = max(temp_max,sim1,sim2)

    # Extra comparisons for alternative names of members
    temp_max = compare_with_alternative_sim(speaker_name, member_name, member_surname, temp_max, greek_names)

    #We compare speaker with member's nickname and surname
    if lower_nickname_in_parenthesis.search(member_name_part) and speaker_nickname=='':

        member_nickname = re.sub ('[()]','',(lower_nickname_in_parenthesis.search(member_name_part)).group())
        sim3 = jellyfish.jaro_winkler_similarity(speaker_name, member_nickname+' '+member_surname)
        sim4 = jellyfish.jaro_winkler_similarity(speaker_name, member_surname+' '+member_nickname)

        temp_max = max(temp_max, sim3, sim4)

    return temp_max



parser = ArgumentParser()
parser.add_argument("-f", "--data_folder",
                    help="relative path to folder of data batch", )
parser.add_argument("-o", "--outpath",
                    help="out csv file relative path")
parser.add_argument("-o2", "--outpath2",
                    help="out csv file relative path2")
args = parser.parse_args()
datapath = args.data_folder
f1_path = args.outpath
f2_path = args.outpath2

# Goal file with all members speeches
f1 = open(f1_path, 'w+', encoding='utf-8', newline = '')

members_df = pd.read_csv('../out_files/all_members_activity.csv', encoding='utf-8')

fnames = open('../out_files/greek_names_alts_only.txt', 'r+', encoding='utf-8')
greek_names = fnames.readlines()

filenames = sorted([f for f in os.listdir(datapath) if not f.startswith('.')])

filename_freqs = defaultdict(int)

record_counter = 0

# REGULAR EXPRESSIONS
#------------------------------------------
speaker_regex = re.compile(r"((\s*[Α-ΩΆ-ΏΪΫΪ́Ϋ́-]+)(\s+[Α-ΩΆ-ΏΪΫΪ́Ϋ́-]+)*\s*(\(.*?\))?\s*\:)")
caps_nickname_in_parenthesis = re.compile(r"(\([Α-ΩΆ-ΏΪΫΪ́Ϋ́]+\))+") #(ΠΑΝΟΣ)
lower_nickname_in_parenthesis = re.compile(r"(\([α-ω]{2,}\))") #(πανος)
text_in_parenthesis = re.compile(r"(\(.*?\)){1}") #(Υπουργός Εσωτερικών)

# Regex for both proedros or proedreuon
proedr_regex = re.compile(
    r"(^(((Π+Ρ(Ο|Ό)+(Ε|Έ))|(Ρ(Ο|Ό)+(Ε|Έ)Δ)|(ΠΡ(Ε|Έ)(Ο|Ό))|(ΠΡ(Ο|Ό)Δ)|(Η ΠΡ(Ο|Ό)(Ε|Έ)ΔΡ)|(ΠΡ(Ε|Έ)Δ))|(ΠΡΟΣΩΡΙΝΗ ΠΡΟΕΔΡΟΣ)|(ΠΡΟΣΩΡΙΝΟΣ ΠΡΟΕΔΡΟΣ)))")

# Regex for proedros only
proedros_regex = re.compile(r"ΠΡ((Ο|Ό|(ΟΟ))(Ε|Έ)|((ΕΟ)|(ΈΟ)|(ΕΌ)|(ΈΌ)))ΔΡΟΣ")
proedreuon_first_speaker = re.compile(r"((\s*[Α-ΩΆ-ΏΪΫΪ́Ϋ́-]+)(\s+\(([Α-ΩΆ-Ώα-ωά-ώϊϋΐΰΪΫΪ́Ϋ́-]\s*)+\))?\s*\:)$")
general_member_regex = re.compile(r"((Β(Ο|Ό)(Υ|Ύ)(Ε|Έ)Λ)|(Β(Ο|Ό)(Υ|Ύ)Λ(Ε|Έ)(Υ|Ύ)?Τ[^(Α|Ά)]))")
left_parenthesis_regex = re.compile(r"\(")
right_parenthesis_regex = re.compile(r"\)")
incomplete_nickname_parenthesis = re.compile(r"\([Α-ΩΆ-ΏΪΫΪ́]{3,}\s")
sitting_terminated_regex = re.compile(r"λ(υ|ύ)εται\s+η\s+συνεδρ(ι|ί)αση")
#------------------------------------------

csv_output = csv.writer(f1)

# csv header
csv_output.writerow(['member_name', 'sitting_date', 'parliamentary_period',
                     'parliamentary_session','parliamentary_sitting',
                     'political_party', 'government', 'member_region', 'roles', 'member_gender',
                     'speaker_info', 'speech'])

# Open a file in order to write down the rows with no files
prob_files = open('../out_files/files_with_content_problems_'+
                  os.path.basename(os.path.normpath(datapath))+'.txt','w+',
                  encoding='utf-8')

for filename in filenames:

    record_counter += 1
    print("File "+str(record_counter)+' from '+ str(len(filenames))+ ' '+filename)

    # Skip duplicate files
    new_name = '_'.join([p for p in filename.split('_') if p!=(filename.split('_')[1])])

    filename_freqs[new_name]+=1
    if filename_freqs[new_name]>1:
        continue #with next iteration of for loop

    name_parts_without_extension = (os.path.splitext(filename)[0]).split('_')
    record_date = name_parts_without_extension[0]
    record_year = record_date.split('-')[0].strip()
    current_record_datetime = dt.strptime(record_date, '%Y-%m-%d')
    current_gov = get_gov(current_record_datetime)

    name_parts_cleaned = [re.sub("[()-]", ' ', part) for part in name_parts_without_extension]
    record_period = re.sub(r"\s\s+",' ',name_parts_cleaned[2].strip())
    record_session = re.sub(r"\s\s+",' ',name_parts_cleaned[3].strip())
    record_sitting = re.sub(r"\s\s+",' ',name_parts_cleaned[4].strip())

    f3 = open(os.path.join(datapath+filename), 'r', encoding='utf-8')
    file_content = f3.read().replace('\n', '')
    file_content = re.sub("\s\s+" , " ", file_content)

    # Creates a list of tuples e.g. (' ΠΡΟΕΔΡΕΥΩΝ (Βαΐτσης Αποστολάτος):', ' ΠΡΟΕΔΡΕΥΩΝ', '', '(Βαΐτσης Αποστολάτος)')
    speakers_groups = re.findall(
        r"((\s*[Α-ΩΆ-ΏΪΫΪ́Ϋ́-]+)(\s+\([Α-ΩΆ-Ώα-ωά-ώϊϋΐΰΪΫΪ́Ϋ́-]+\))?(\s+[Α-ΩΆ-ΏΪΫΪ́Ϋ́]+)?(\s+[Α-ΩΆ-ΏΪΫΪ́Ϋ́-]+)*\s*(\(.*?\))?\s*\:)",
        file_content)

    # Keep only first full match case of findall
    speakers = [speaker[0] for speaker in speakers_groups]

    # Discard introductory text before first speaker
    # Use split with maxsplit number 1 in order to split at first occurrence
    try:
        file_content = file_content.split(speakers[0], 1)[1]
    except:
        prob_files.write(filename + " \n")
        continue # proceed to next iteration/filename

    for i in range(len(speakers)):

        # If not last speaker
        if i < (len(speakers)-1):
            speaker = speakers[i]
            speech,file_content = file_content.split(speakers[i+1], 1)
        else:
            speaker = speakers[i]
            speech = file_content

        # special treatment for first speaker who is usually proedreuon
        if i == 0:
            if proedreuon_first_speaker.search(speaker.strip()):
                speaker = proedreuon_first_speaker.search(speaker.strip()).group()

        # remove parenthesis text which is usually descriptions of procedures
        speech = re.sub(text_in_parenthesis, " ", speech)

        # Clean speaker
        speaker = speaker.strip()
        speaker = re.sub("\s\s+", " ", speaker)

        speaker_info=np.nan
        speaker_nickname=''

        #in case the speaker name is like "ΠΡΟΕΔΡΕΥΩΝ (Παναγιώτης Ν. Κρητικός):"
        # or like ΠΡΟΣΩΡΙΝΟΣ ΠΡΟΕΔΡΟΣ (Ιωάννης Τραγάκης):
        if proedr_regex.search(speaker):

            # Hand-picked wrong cases
            if any(mistaken in speaker for mistaken in ['ΤΗΛΕΦΩΝΟ', 'ΓΡΑΜΜΑΤΕΙΣ', 'ΠΡΟΕΚΟΠΗΣ']):
                continue # to next iteration/speaker

            # For proedreuon
            if not proedros_regex.search(speaker):
                speaker_info = 'προεδρευων'

            # For proedros
            else:
                # if the person in proedros
                if 'ΠΡΟΣΩΡΙΝ' in speaker:
                    speaker_info = 'προσωρινος προεδρος'
                else:
                    speaker_info = 'προεδρος'

            segments = speaker.split('(')
            speaker = ''.join(segments[1:])

            # for cases where the name of the person is not mentioned
            if len(speaker)<3:
                speaker = np.nan
                party = np.nan
                speaker_gender = np.nan
                speaker_region = np.nan
                roles = np.nan
                csv_output.writerow([speaker, current_record_datetime.strftime('%d/%m/%Y'),
                                     record_period, record_session, record_sitting,
                                     party, current_gov, speaker_region, roles,
                                     speaker_gender, speaker_info, speech])

                continue # to next iteration/speaker

        if speaker.startswith('ΜΑΡΤΥΣ'):
            speaker = speaker.replace('ΜΑΡΤΥΣ', '')
            speaker = re.sub("[()]",'', speaker)
            speaker_info = 'μαρτυς'

            if len(speaker)<3: #for cases where the name of the person is not mentioned
                speaker = np.nan
                party = np.nan
                speaker_gender = np.nan
                speaker_region = np.nan
                roles = np.nan
                csv_output.writerow([speaker, current_record_datetime.strftime('%d/%m/%Y'), record_period,
                                     record_session, record_sitting, party, current_gov,
                                     speaker_region, roles, speaker_gender,
                                     speaker_info, speech])

                continue # to next iteration/speaker

        if general_member_regex.search(speaker):
            speaker = (re.sub("[():'’`΄‘.]", '', speaker)).lower()
            speaker = speaker.translate(str.maketrans('άέόώήίϊΐiύϋΰ', 'αεοωηιιιιυυυ'))
            if 'εφηβοι' in speaker:
                continue # to next speaker
            else:
                party = party_of_generic_reference(speaker)
                speaker = np.nan
                speaker_gender = np.nan
                speaker_region = np.nan

                # When the closing speech is assigned to generic members instead of the proedreuon
                # which is usually the case when proedreuon is not mentioned as the closing speaker
                # we remove the standard closing talk of the sitting from the generic members speech
                if sitting_terminated_regex.search(speech):
                    speech = \
                    re.split("(μ|Μ)ε\s+(τη|την)\s+(συναινεση|συναίνεση)\s+του\s+((σ|Σ)(ω|ώ)ματος|(τ|Τ)μ(η|ή)ματος)",
                             speech)[0]

                speaker_info = 'βουλευτης/ες'
                roles = np.nan
                csv_output.writerow([speaker, current_record_datetime.strftime('%d/%m/%Y'), record_period,
                                     record_session, record_sitting, party, current_gov,
                                     speaker_region, roles, speaker_gender,
                                     speaker_info, speech])

                continue

        # continue
        if speaker != '':

            # Exclude very large malformed text that is not a speaker
            if len(speaker) < 200:
                speaker, speaker_nickname = separate_nickname_incomplete_parenthesis(speaker, speaker_nickname)

                if caps_nickname_in_parenthesis.search(speaker):
                    speaker, speaker_nickname = separate_nickname(speaker)

                if text_in_parenthesis.search(speaker):
                    speaker, speaker_info = separate_explanatory_parenthesis(speaker)
                    speaker_info = format_speaker_info(speaker_info)

                speaker_name = text_formatting(speaker)
                speaker_name = speaker_name_corrections(speaker_name)

                # Remove 1-2 letter characters
                speaker_name = ' '.join([word for word in speaker_name.split(' ') if len(word) > 2])

                max_sim = 0

                for index, row in members_df.iterrows():

                    member_start_date = dt.strptime(row.member_start_date, '%Y-%m-%d')
                    member_end_date = dt.strptime(row.member_end_date, '%Y-%m-%d')

                    if member_start_date <= current_record_datetime <= member_end_date:

                        member_name_part = row.member_name
                        member_party = row.political_party
                        member_region = row.administrative_region
                        member_gender = row.gender
                        member_gov = row.government_name
                        roles = ast.literal_eval(row.roles)

                        temp_max = compute_max_similarity(speaker_name, speaker_nickname, member_name_part)

                        if temp_max > max_sim:
                            max_sim = temp_max
                            max_member_name_part = member_name_part
                            max_member_party = member_party
                            max_member_region = member_region
                            max_member_gender = member_gender
                            max_member_roles = roles

                # Strict hand-picked similarity threshold to avoid false positives
                if max_sim > 0.95:

                    max_member_roles = keep_roles_at_date(max_member_roles, current_record_datetime)

                    csv_output.writerow([max_member_name_part, current_record_datetime.strftime('%d/%m/%Y'),
                                         record_period, record_session, record_sitting, max_member_party,
                                         current_gov, max_member_region, max_member_roles, max_member_gender,
                                         speaker_info, speech])

    f3.close()

prob_files.close()
f1.close()

df = pd.read_csv(f1_path, encoding='utf-8')

# Remove in period column the string part '-presided-parliamentary-republic+'
df['parliamentary_period'].replace({"-presided-parliamentary-republic_": '_'}, inplace=True, regex=True)

# Correct order of sitting date column
df['sitting_date'].replace({"-presided-parliamentary-republic_": '_'}, inplace=True, regex=True)

if (df[df.apply(lambda r: r.str.contains('presided').any(), axis=1)]).shape[0] == 0:
    print('Check 3 ok')
else:
    print('String \'presided\' is still somewhere in the data')

# Replace date '93 with 1993
df['parliamentary_session'].replace({"'": '19'}, inplace=True, regex=True)

# Check if members with nan name have nan roles
mask = ((df.member_name.isnull()))
if str(set(df.loc[mask, 'roles'].to_list())) == '{nan}':
    print('Check 1 ok')
else:
    print('Roles column of one or more nan member names are not nan')

# Check if members with filled name have not nan roles
mask = ((df.member_name.notnull()))
if np.nan not in (df.loc[mask, 'roles'].to_list()):
    print('Check 2 ok')
else:
    print('Entries with nan roles have filled member names when role should be \'βουλευτης\'')

df.to_csv(f2_path, encoding='utf-8', index=False, na_rep=np.nan)

endtime = dt.now()
print('Comparison lasted from '+str(starttime)+' until '+str(endtime)+'.')
