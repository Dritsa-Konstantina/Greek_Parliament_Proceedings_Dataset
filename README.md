# Greek_Parliament_proceedings_dataset

This dataset originated from the work implemented during the course of the Master thesis entitled "Speech quality and sentiment analysis on the Hellenic Parliament proceedings" at the Athens University of Economics & Business in 2018. It has been updated multiple times since then, in order for the best result to be achieved.

It includes 1,194,407 speeches of Greek parliament members with a total volume of 2.15 GB, that where exported from 5,118 parliamentary sitting record files and extend chronologically from 1989 up to 2019.

The dataset was created with the three following basic steps:

 - Collection of the record files of the parliament proceedings that are published on the website of the Greek Parliament https://www.hellenicparliament.gr/Praktika/Synedriaseis-Olomeleias
 - Collection of the official published names of all the members of the Hellenic Parliament from the website of the Greek Parliament https://www.hellenicparliament.gr/Vouleftes/Diatelesantes-Vouleftes-Apo-Ti-Metapolitefsi-Os-Simera/
 - Detecting speakers and their corresponding speeches from the records and matching the speaker names provided in the records with the official parliament member names.

The dataset consists of a csv file in UTF-8 encoding and includes the following columns of data:

member_name: The official name of the parliament member that talked during a sitting.

sitting_date: The date that the sitting took place. There are cases were more than one sittings took place at the same date.

<b>parliamentary_period:</b> The name and/or number of the parliamentary period that the speech took place in. A parliamentary period includes multiple parliamentary sessions.

parliamentary_session: The name and/or number of the parliamentary session that the speech took place in. A parliamentary session includes multiple parliamentary sittings.

parliamentary_sitting: The name and/or number of the parliamentary sitting that the speech took place in.

political_party: The political party that the speaker belongs to.

speaker_info: Information about the speaker extracted from the text of the proceeding/sitting record that refers to the parliamentary role of the speaker such as Chairman of the Parliament, Finance Minister or similar.

speech: The speech that the member made during the sitting of the Greek Parliament.

Any fields that do not include information, due to omissions in the record files, are filled with a NaN value, apart from the speech field, which in such cases remains an empty string.

Enjoy!
