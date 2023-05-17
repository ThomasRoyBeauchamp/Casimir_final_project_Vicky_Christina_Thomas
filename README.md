# Casimir_final_project_Vicky_Christina_Thomas
Final Project for Casimir Programming course. We are programming a script
that will be searching throught websites to find suitable summer schools and conferences for quantum information.

Todo:

-Navigate to the webpages 'id': <eventList> to get the hyperlinks for each conference
-Navigate to each conference webpage and compare the key_words in keywords.py with the "conference tags" and the description
-If we we have more than 3 matches we move on to extract the date and place, place and official website of the conference
-We navigate to the the programm page of the official website of the conference and search for key_authors
-If we have a match or more we add it as as a comment in the email
-Write and and send the email containing: dates, place, website and potential speakes that are on our key_author list

Structure of the email:

Dear Qutech,

this is a list of potentially interesting conferences coming up in the field
of quantum information:
-<print title><print url>(notable speakers <print list of speakers that match with key_authors>

Best regards,

