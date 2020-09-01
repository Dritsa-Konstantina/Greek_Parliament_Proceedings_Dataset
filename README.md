# Greek_Parliament_proceedings_dataset

Script order:

1. web_crawler_for_proceeding_files.py: Download record files from https://www.hellenicparliament.gr/Praktika/Synedriaseis-Olomeleias and change the file name to "recordDate_id_periodNo_sessionNo_sittingNo.ext" 
2. convert2txt.py: Convert all types of downloaded record files (pdf, doc, docx) to text format with the use of tika-app-1.20.jar and rename the converted files from Greek to English.
3. web_crawler_for_parliament_members.py: Download information of the Parliament Members from the dropdown list at https://www.hellenicparliament.gr/Vouleftes/Diatelesantes-Vouleftes-Apo-Ti-Metapolitefsi-Os-Simera/. Create a file original_members_data.csv
4. members_data_cleaner.py: Clean and format the file original_members_data.csv. Create a new file members_activity_1989onwards.csv
5. add_gender_to_members.py: Add gender column to the members_activity_1989onwards.csv with the use of the files "female_names_alternatives_gr.txt" and "male_names_alternatives_gr.txt" and create the file "members_activity_1989onwards_with_gender.csv"
6. ggk_crawler.py: Crawl the website https://gslegal.gov.gr/?page_id=776&sort=time and collect information about all the governments from 1989 up to 2020 and all the members that were assigned parliamentary roles. Create the files governments_1989onwards.csv (with information only about the governments and their start and end dates) and the "initial_ggk_data.csv" with the crawled raw data from the website...
7. clean_ggk_data.py: Clean the file "initial_ggk_data.csv". Convert names and surnames from genitive to nominative case and add gender with the use of the files crawled from Wikipedia ("male_name_cases_populated.json", "female_name_cases_populated.json", "male_surname_cases_populated.json"). Make corrections in roles, member names, entries and create a file "formatted_roles_ggk_data.csv" with columns ['member_name', 'role', 'role_start_date', 'role_end_date', 'gender']
8. join_members_activity.py: Concatenate three files with information of parliament members and extra parliamentary members. The files are: "members_activity_1989onwards_with_gender.csv" (includes parliament members), "formatted_roles_ggk_data.csv" (includes all government members that have been assigned with a government role but may not have been necessarily elected as parliament memebrs) and "extra_roles_manually.csv" (includes manually collected additional roles from Wikipedia such as Chairman of the Parliament, party leaders etc). The output of this script is the file "all_members_activity.csv"
9. member_speech_matcher.py: Extract speeches from record files and match them to the official parliament or government member. After the detection of a speech in a record file with the use of regular expressions, search the detected speaker in the file "all_members_activity.csv". For the string comparison between names, the file "greek_names_alts_only.txt" is used with a list of Greek names and their alternatives. The output file is the "tell_all.csv" with columns ['member_name', 'sitting_date', 'parliamentary_period', 'parliamentary_session', 'parliamentary_sitting', 'political_party', 'government', 'member_region','roles', 'member_gender','speaker_info', 'speech']
10. fill_proedr_names.py: fills in the names of chairmen in the same sittings when they are not mentioned in a specific speech, as long as the sitting has only one chairman.
11. csv_concat.py: concatenates all "tell_all.csv" files created in case the script "member_speech_matcher.py" is run in parallel for time-optimization and created different csvs for different batches of the data.


Requirements
- Libraries from requirements.txt
- Python version 3.6.8
- WebDriver for Chrome