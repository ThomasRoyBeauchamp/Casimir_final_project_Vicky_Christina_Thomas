"""
Final_project_Vicky_Christina_Thomas.py
This script gets the latest conferences and summer schools in quantum information and sends an email with the important deadlines and info to the recepients.
Adapted from 
Marie-Christine Roehsner, Julia Brevoord, Julius Fischer (Casimir Research School Programming Course 2022) by
Christina Ioannou, Thomas Beauchamp and Victoria Dominguez Tubio (Casimir Reseach School Programming Course 2023)
"""

from datetime import timedelta
from datetime import date
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
import smtplib
import requests
import os

from tqdm import tqdm

from Conference_Hunting import Conference, get_all_conferences

from key_words import key_authors, key_words, key_email_addresses

TO = key_email_addresses #TO = ["J.M.Brevoord@tudelft.nl", "M.Roehsner@tudelft.nl","julius.fischer@tudelft.nl"]

search_string = "https://conferenceindex.org/conferences/quantum-physics"

search_string_1 = "https://quantum.info/conf/"


def get_computer_name():
    """Find the computer name that executes this script
    
    Uses some os methods to find the computer name

    Parameters
    ----------
    None
    
    Returns
    -------
    user : str
        user name of the computer
    """
    for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user = os.environ.get(name)
        if user:
            return user
    # If not user from os.environ.get()
    import pwd
    return pwd.getpwuid(os.getuid())[0]


all_dodgy_conferences = get_all_conferences()


prog = tqdm(total=len(all_dodgy_conferences), desc="Finding Details")

c: Conference
for c in all_dodgy_conferences: #Gets details of conferences
    c.retrieve_details()
    prog.update()

prog.close()
all_dodgy_conferences.match_keywords(number_of_keywords=12) #Filters all_confs down to only those conferences with at least (number_of_keywords) keywords





prog = tqdm(total=len(all_dodgy_conferences), desc="Finding Speakers")
for c in all_dodgy_conferences:
    c.retrieve_speakers() #Gets speakers of remaining conferences
    prog.update()



soup=f'''Dear Julius,

this is a list of potentially predatory conferences coming up in the field
of quantum information wothin the next two to six months:

{all_dodgy_conferences}

We know now that we should have done a bit more reasearch before choosing
the particular website but we hope future generations of PhDs might be 
interested in adapting to a different website. The code strucutre should not 
be too hard to adapt.

Let us know if you have any questions about our code.


 
Best regards,

Vicky, Thomas and Christina'''

print(soup, 'html')


#Send email
SUBJECT = "Your favourite dodgy conferences".format(date.today())
FROM = "c.i.ioannou@tudelft.nl"

server = smtplib.SMTP('smtp.tudelft.nl')

for to in TO:
    msg = MIMEText(str(soup), 'plain')
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = to

    try:
        server.sendmail(FROM, to, msg.as_string())
    except:
        print("Sending email to {} failed.".format(to))

server.quit()


