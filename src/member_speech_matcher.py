# -*- coding: utf-8 -*-
import os
import re
import jellyfish
from collections import defaultdict
import csv
import numpy as np
import time
from datetime import datetime as dt
from argparse import ArgumentParser

starttime = dt.now()

#Cleaning and formatting speakers data
def text_formatting(text):
    text = re.sub("[():'’`΄‘]",' ', text)
    text = re.sub('\t+' , ' ', text)
    text = text.lstrip()
    text = text.rstrip()
    text = re.sub('\s\s+' , ' ', text)
    text = re.sub('\s*(-|–)\s*' , '-', text)
    text = text.lower()
    text = text.translate(str.maketrans('άέόώήίϊΐiύϋΰ','αεοωηιιιιυυυ'))
    text = text.translate(str.maketrans('akebyolruxtvhmnz','ακεβυολρυχτνημνζ'))
    return(text)

def speaker_name_corrections(name):
    if 'γενηματα' in name:
        name = name.replace('γενηματα', 'γεννηματα')
    if 'βαρουφακης' in name:
        name = name.replace('γιαννης', 'γιανης')
    if 'ζουραρις' in name:
        name = name.replace('ζουραρις','ζουραρης')
    return(name)

# for example ΠΟΛΛΟΙ ΒΟΥΛΕΥΤΕΣ (από την πτέρυγα του ΠΑ.ΣΟ.Κ.):,2006
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
    lefts=0
    rights=0
    if left_parenthesis_regex.search(speaker):
        lefts = len(re.findall(left_parenthesis_regex,speaker))
    if right_parenthesis_regex.search(speaker):
        rights = len(re.findall(right_parenthesis_regex,speaker))
    if (lefts-rights)>0:
        if incomplete_nickname_parenthesis.search(speaker):

            speaker_nickname = (incomplete_nickname_parenthesis.search(speaker)).group()
            speaker_nickname = text_formatting(speaker_nickname)
            speaker = re.sub(incomplete_nickname_parenthesis, '', speaker)
    return speaker, speaker_nickname

# Keep separately the nickname of the speaker
def separate_nickname(speaker, speaker_nickname):
    speaker_nickname = (caps_nickname_in_parenthesis.search(speaker)).group()
    speaker_nickname = text_formatting(speaker_nickname)
    speaker = re.sub(caps_nickname_in_parenthesis, '', speaker)
    return speaker, speaker_nickname


# Keep separately the explanatory parenthesis text of the speaker
def separate_explanatory_parenthesis(speaker):
    speaker_info = (text_in_parenthesis.search(speaker)).group()
    speaker = re.sub(text_in_parenthesis, '', speaker)
    return speaker,speaker_info

def format_speaker_info(speaker_info):
    speaker_info = text_formatting(speaker_info)
    speaker_info = speaker_info.replace('υφυπ.',' υφυπουργος ')
    speaker_info = speaker_info.replace('υπ.',' υπουργος ')
    speaker_info = speaker_info.replace('&',' και ')
    speaker_info = re.sub('\s\s+' , ' ', speaker_info)
    speaker_info = speaker_info.lstrip()
    speaker_info = speaker_info.rstrip()
    return speaker_info

# compare temp max with similarity of the member's name alternatives with the speaker name
def compare_with_alternative_sim(speaker_name, member_name, member_surname, temp_max, greek_names):

    # each row in the greek_names data is unique concerning the first name of the row
    for line in greek_names:

        name_list = (line.strip()).split(',')

        # if member name has alternatives
        if name_list[0]==member_name:

            # keep alternatives of the name
            name_list.remove(member_name)

            for alternative_name in name_list:
                alternative_sim1 = jellyfish.jaro_winkler(speaker_name, alternative_name+' '+member_surname)
                alternative_sim2 = jellyfish.jaro_winkler(speaker_name, member_surname + ' ' + alternative_name)
                temp_max = max(temp_max,alternative_sim1, alternative_sim2)

            break #if true, break the for loop and proceed to return temp pax

    return(temp_max)

def compute_max_similarity(speaker_name, speaker_nickname, member_name_part):

    member_surname = member_name_part.split(' ')[0]
    member_name = member_name_part.split(' ')[2]
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
            sim5 = jellyfish.jaro_winkler(speaker_name, member_name1+' '+member_surname)
            sim6 = jellyfish.jaro_winkler(speaker_name, member_surname+' '+member_name1)
            sim7 = jellyfish.jaro_winkler(speaker_name, member_name2+' '+member_surname)
            sim8 = jellyfish.jaro_winkler(speaker_name, member_surname+' '+member_name2)

            temp_max = max(temp_max, sim5, sim6, sim7, sim8)

            # Extra comparisons for alternative names of members
            temp_max = compare_with_alternative_sim(speaker_name, member_name1, member_surname, temp_max, greek_names)
            temp_max = compare_with_alternative_sim(speaker_name, member_name2, member_surname, temp_max, greek_names)


            # do the following extra for three first names
            # for example κουικ φιλιππου τερενς-σπενσερ-νικολαος

            if len(member_name.split('-'))==3:
                sim9 = jellyfish.jaro_winkler(speaker_name, member_name3+' '+member_surname)
                sim10 = jellyfish.jaro_winkler(speaker_name, member_surname+' '+member_name3)
                temp_max = max(temp_max, sim9, sim10)

                # Extra comparisons for alternative names of members
                temp_max = compare_with_alternative_sim(speaker_name, member_name3, member_surname, temp_max,
                                                        greek_names)

        else:
            # If member has more than one first names and two surnames, compare each one separately
            member_surname1,member_surname2=member_surname.split('-')
            sim5 = jellyfish.jaro_winkler(speaker_name, member_name1+' '+member_surname1)
            sim6 = jellyfish.jaro_winkler(speaker_name, member_surname1+' '+member_name1)
            sim7 = jellyfish.jaro_winkler(speaker_name, member_name1+' '+member_surname2)
            sim8 = jellyfish.jaro_winkler(speaker_name, member_surname2+' '+member_name1)
            sim9 = jellyfish.jaro_winkler(speaker_name, member_name2+' '+member_surname1)
            sim10 = jellyfish.jaro_winkler(speaker_name, member_surname1+' '+member_name2)
            sim11 = jellyfish.jaro_winkler(speaker_name, member_name2+' '+member_surname2)
            sim12 = jellyfish.jaro_winkler(speaker_name, member_surname2+' '+member_name2)

            temp_max = max(temp_max, sim5, sim6, sim7, sim8, sim9, sim10, sim11, sim12)

            # Extra comparisons for alternative names of members
            temp_max = compare_with_alternative_sim(speaker_name, member_name1, member_surname1, temp_max, greek_names)
            temp_max = compare_with_alternative_sim(speaker_name, member_name1, member_surname2, temp_max, greek_names)
            temp_max = compare_with_alternative_sim(speaker_name, member_name2, member_surname1, temp_max, greek_names)
            temp_max = compare_with_alternative_sim(speaker_name, member_name2, member_surname2, temp_max, greek_names)

    # If member has one first name and two surnames
    elif '-' in member_surname:
        member_surname1,member_surname2=member_surname.split('-')
        sim5 = jellyfish.jaro_winkler(speaker_name, member_name+' '+member_surname1)
        sim6 = jellyfish.jaro_winkler(speaker_name, member_surname1+' '+member_name)
        sim7 = jellyfish.jaro_winkler(speaker_name, member_name+' '+member_surname2)
        sim8 = jellyfish.jaro_winkler(speaker_name, member_surname2+' '+member_name)

        temp_max = max(temp_max, sim5, sim6, sim7, sim8)

        # Extra comparisons for alternative names of members
        temp_max = compare_with_alternative_sim(speaker_name, member_name, member_surname1, temp_max, greek_names)
        temp_max = compare_with_alternative_sim(speaker_name, member_name, member_surname2, temp_max, greek_names)

        #If member has available nickname and two surnames
        if lower_nickname_in_parenthesis.search(member_name_part) and speaker_nickname=='':

            member_nickname = re.sub ('[()]','',(lower_nickname_in_parenthesis.search(member_name_part)).group())
            sim9 = jellyfish.jaro_winkler(speaker_name, member_nickname+' '+member_surname1)
            sim10 = jellyfish.jaro_winkler(speaker_name, member_surname1+' '+member_nickname)
            sim11 = jellyfish.jaro_winkler(speaker_name, member_nickname+' '+member_surname2)
            sim12 = jellyfish.jaro_winkler(speaker_name, member_surname2+' '+member_nickname)

            temp_max = max(temp_max, sim9, sim10, sim11, sim12)

    # Remove '-' for sim1, sim2 best comparisons
    member_name = member_name.replace('-', ' ')
    member_surname = member_surname.replace('-', ' ')

    #M ake comparisons of speaker with members' names and reversed members' names
    sim1 = jellyfish.jaro_winkler(speaker_name, member_name+' '+member_surname)
    sim2 = jellyfish.jaro_winkler(speaker_name, member_surname+' '+member_name)
    temp_max = max(temp_max,sim1,sim2)

    # Extra comparisons for alternative names of members
    temp_max = compare_with_alternative_sim(speaker_name, member_name, member_surname, temp_max, greek_names)


    # Compare speaker with member's nickname and surname
    if lower_nickname_in_parenthesis.search(member_name_part) and speaker_nickname=='':

        member_nickname = re.sub ('[()]','',(lower_nickname_in_parenthesis.search(member_name_part)).group())
        sim3 = jellyfish.jaro_winkler(speaker_name, member_nickname+' '+member_surname)
        sim4 = jellyfish.jaro_winkler(speaker_name, member_surname+' '+member_nickname)

        temp_max = max(temp_max, sim3, sim4)

    return temp_max


# Use Example:
# python member_speech_matcher.py -f '../_data/batch_0/' -o '../out_files/tell_all_batch_0.csv'

parser = ArgumentParser()
parser.add_argument("-f", "--data_folder",
                    help="relative path to folder of data batch", )
parser.add_argument("-o", "--outpath",
                    help="out csv file relative path")
args = parser.parse_args()
datapath = args.data_folder
f1_path = args.outpath

# Goal file with all members speeches
f1 = open(f1_path, 'w+', encoding='utf-8', newline = '')
f2 = open('../out_files/members_activity_1989onwards_with_gender.csv', 'r+', encoding='utf-8')
member_reader = csv.reader(f2)
next(member_reader) #skip headers
fnames = open('../out_files/greek_names_alts_only.txt', 'r+', encoding='utf-8')
greek_names = fnames.readlines()
filenames = sorted([f for f in os.listdir(datapath) if not f.startswith('.')])
filename_freqs = defaultdict(int)

record_counter = 0

speaker_regex = re.compile(r"((\s*[Α-ΩΆ-ΏΪΫΪ́Ϋ́-]+)(\s+[Α-ΩΆ-ΏΪΫΪ́Ϋ́-]+)*\s*(\(.*?\))?\s*\:)")
caps_nickname_in_parenthesis = re.compile(r"(\([Α-ΩΆ-ΏΪΫΪ́Ϋ́]+\))+") #(ΠΑΝΟΣ)
lower_nickname_in_parenthesis = re.compile(r"(\([α-ω]{2,}\))") #(πανος)
text_in_parenthesis = re.compile(r"(\(.*?\)){1}") #(Υπουργός Εσωτερικών)

# Regex for both proedros or proedreuon
proedr_regex = re.compile(
    r"(^(((Π+Ρ(Ο|Ό)+(Ε|Έ))|(Ρ(Ο|Ό)+(Ε|Έ)Δ)|(ΠΡ(Ε|Έ)(Ο|Ό))|(ΠΡ(Ο|Ό)Δ)|(Η ΠΡ(Ο|Ό)(Ε|Έ)ΔΡ)|(ΠΡ(Ε|Έ)Δ))|(ΠΡΟΣΩΡΙΝΗ ΠΡΟΕΔΡΟΣ)|(ΠΡΟΣΩΡΙΝΟΣ ΠΡΟΕΔΡΟΣ)))")

proedros_regex = re.compile(r"ΠΡ((Ο|Ό|(ΟΟ))(Ε|Έ)|((ΕΟ)|(ΈΟ)|(ΕΌ)|(ΈΌ)))ΔΡΟΣ")
proedreuon_first_speaker = re.compile(r"((\s*[Α-ΩΆ-ΏΪΫΪ́Ϋ́-]+)(\s+\(([Α-ΩΆ-Ώα-ωά-ώϊϋΐΰΪΫΪ́Ϋ́-]\s*)+\))?\s*\:)$")
general_member_regex = re.compile(r"((Β(Ο|Ό)(Υ|Ύ)(Ε|Έ)Λ)|(Β(Ο|Ό)(Υ|Ύ)Λ(Ε|Έ)(Υ|Ύ)?Τ[^(Α|Ά)]))")
left_parenthesis_regex = re.compile(r"\(")
right_parenthesis_regex = re.compile(r"\)")
incomplete_nickname_parenthesis = re.compile(r"\([Α-ΩΆ-ΏΪΫΪ́]{3,}\s")
sitting_terminated_regex = re.compile(r"λ(υ|ύ)εται\s+η\s+συνεδρ(ι|ί)αση")

csv_output = csv.writer(f1)

csv_output.writerow(['member_name', 'sitting_date', 'parliamentary_period',
                     'parliamentary_session','parliamentary_sitting',
                     'political_party', 'member_region', 'member_gender',
                     'speaker_info', 'speech'])

#Open a file in order to write down the rows with no files
prob_files = open('../out_files/files_with_content_problems_'+
                  os.path.basename(os.path.normpath(datapath))+'.txt','w+',
                  encoding='utf-8')

for filename in filenames:

    record_counter+=1
    print("File "+str(record_counter)+' from '+ str(len(filenames)-1)+ ' '+filename)

    # Skip duplicate files
    new_name = '_'.join([p for p in filename.split('_') if p!=(filename.split('_')[1])])

    filename_freqs[new_name]+=1
    if filename_freqs[new_name]>1:
        continue

    name_parts_without_extension = (os.path.splitext(filename)[0]).split('_')
    record_date = name_parts_without_extension[0]
    record_year = record_date.split('-')[0].strip()

    name_parts_cleaned = [re.sub("[()-]", ' ', part) for part in name_parts_without_extension]
    record_period = re.sub(r"\s\s+",' ',name_parts_cleaned[2].strip())
    record_session = re.sub(r"\s\s+",' ',name_parts_cleaned[3].strip())
    record_sitting = re.sub(r"\s\s+",' ',name_parts_cleaned[4].strip())

    f3 = open(os.path.join(datapath+filename), 'r', encoding='utf-8')
    file_content = f3.read().replace('\n', '')
    file_content = re.sub("\s\s+" , " ", file_content)

    speakers_groups = re.findall(
        r"((\s*[Α-ΩΆ-ΏΪΫΪ́Ϋ́-]+)(\s+\([Α-ΩΆ-Ώα-ωά-ώϊϋΐΰΪΫΪ́Ϋ́-]+\))?(\s+[Α-ΩΆ-ΏΪΫΪ́Ϋ́]+)?(\s+[Α-ΩΆ-ΏΪΫΪ́Ϋ́-]+)*\s*(\(.*?\))?\s*\:)",
        file_content)


    speakers = [speaker[0] for speaker in speakers_groups]

    # Discard introductory text before first speaker
    # Use split with maxsplit number 1 in order to split at first occurrence
    try:
        file_content = file_content.split(speakers[0], 1)[1]

    except:
        prob_files.write(filename + " \n")
        continue

    for i in range(len(speakers)):

        # If not last speaker
        if i < (len(speakers)-1):
            speaker = speakers[i]
            speech,file_content = file_content.split(speakers[i+1], 1)
        else:
            speaker = speakers[i]
            speech = file_content

        # special treatment for first speaker who is usually προεδρευων
        if i == 0:
            if proedreuon_first_speaker.search(speaker.strip()):
                speaker = proedreuon_first_speaker.search(speaker.strip()).group()

        # remove parenthesis text which is usually descriptions of procedures
        speech = re.sub(text_in_parenthesis, " ", speech)

        #Clean speaker
        speaker = speaker.strip()
        speaker = re.sub("\s\s+" , " ", speaker)

        speaker_info=np.nan
        speaker_nickname=''

        #in case the speaker name is like "ΠΡΟΕΔΡΕΥΩΝ (Παναγιώτης Ν. Κρητικός):"
        # or like ΠΡΟΣΩΡΙΝΟΣ ΠΡΟΕΔΡΟΣ (Ιωάννης Τραγάκης):
        if proedr_regex.search(speaker):

            # Hand-picked wrong cases
            if any(mistaken in speaker for mistaken in ['ΤΗΛΕΦΩΝΟ', 'ΓΡΑΜΜΑΤΕΙΣ', 'ΠΡΟΕΚΟΠΗΣ']):
                continue

            # For προεδρευων
            if not proedros_regex.search(speaker):
                speaker_info = 'προεδρευων'

            # For προεδρος
            else:

                if 'ΠΡΟΣΩΡΙΝ' in speaker:
                    speaker_info = 'προσωρινος προεδρος'
                else:
                    speaker_info = 'προεδρος'

            segments = speaker.split('(')
            speaker = ''.join(segments[1:])
            if len(speaker)<3: #for cases where the name of the person is not mentioned
                speaker = np.nan
                party = np.nan
                speaker_gender = np.nan
                speaker_region = np.nan
                csv_output.writerow([speaker, record_date, record_period,
                                     record_session, record_sitting, party,
                                     speaker_region, speaker_gender,
                                     speaker_info, speech])

                continue

        if speaker.startswith('ΜΑΡΤΥΣ'):
            speaker = speaker.replace('ΜΑΡΤΥΣ','')
            speaker = re.sub("[()]",'', speaker)
            speaker_info = 'μαρτυς'

            if len(speaker)<3: #for cases where the name of the person is not mentioned
                speaker=np.nan
                party = np.nan
                speaker_gender = np.nan
                speaker_region = np.nan
                csv_output.writerow([speaker, record_date, record_period,
                                     record_session, record_sitting, party,
                                     speaker_region, speaker_gender,
                                     speaker_info, speech])

                continue

        if general_member_regex.search(speaker):
            speaker = (re.sub("[():'’`΄‘.]", '', speaker)).lower()
            speaker = speaker.translate(str.maketrans('άέόώήίϊΐiύϋΰ', 'αεοωηιιιιυυυ'))
            if 'εφηβοι' in speaker:
                continue
            else:
                party = party_of_generic_reference(speaker)
                speaker = np.nan
                speaker_gender = np.nan
                speaker_region = np.nan

                # When the closing speech is assigned to generic members instead of the προεδρευων
                # which is usually the case when προεδρευων is not mentioned as the closing speaker
                # we remove the standard closing talk of the sitting from the generic members speech
                if sitting_terminated_regex.search(speech):
                    speech = \
                    re.split("(μ|Μ)ε\s+(τη|την)\s+(συναινεση|συναίνεση)\s+του\s+((σ|Σ)(ω|ώ)ματος|(τ|Τ)μ(η|ή)ματος)",
                             speech)[0]

                speaker_info = 'βουλευτης/ες'
                csv_output.writerow([speaker, record_date, record_period,
                                     record_session, record_sitting, party,
                                     speaker_region, speaker_gender,
                                     speaker_info, speech])
                continue

        if speaker!='':

            speaker, speaker_nickname = separate_nickname_incomplete_parenthesis(speaker,speaker_nickname)

            if caps_nickname_in_parenthesis.search(speaker):
                speaker, speaker_nickname = separate_nickname(speaker,speaker_nickname)

            if text_in_parenthesis.search(speaker):
                speaker, speaker_info = separate_explanatory_parenthesis(speaker)
                speaker_info = format_speaker_info(speaker_info)

            speaker_name = text_formatting(speaker)
            speaker_name = speaker_name_corrections(speaker_name)

            # Remove 1-2 letter characters
            speaker_name = ' '.join( [word for word in speaker_name.split(' ') if len(word)>2] )

            max_sim = 0

            f2.seek(0)
            next(member_reader)  # skip headers

            for member_line in member_reader:

                member_start_date = dt.strptime(member_line[1], '%Y-%m-%d')
                member_end_date = dt.strptime(member_line[2], '%Y-%m-%d')

                this_record_date = dt.strptime(record_date, '%Y-%m-%d')

                if member_start_date <= this_record_date <= member_end_date:

                    member_name_part=member_line[0]
                    member_party = member_line[3]
                    member_region = member_line[4]
                    member_gender = member_line[5]

                    temp_max = compute_max_similarity(speaker_name, speaker_nickname, member_name_part)

                    if temp_max>max_sim:
                        max_sim=temp_max
                        max_member_name_part = member_name_part
                        max_member_party = member_party
                        max_member_region = member_region
                        max_member_gender = member_gender

            if max_sim>0.95:
                csv_output.writerow([max_member_name_part, record_date, record_period,
                                     record_session, record_sitting, max_member_party,
                                     max_member_region, max_member_gender,
                                     speaker_info, speech])

    f3.close()

prob_files.close()
f1.close()
f2.close()

endtime = dt.now()
print('Comparison lasted from '+str(starttime)+' until '+str(endtime)+'.')