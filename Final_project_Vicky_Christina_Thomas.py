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

from Conference_Hunting import Conference, get_all_conference_pages

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


def find_favourite_papers(articles, favourites, html_class, rank_list):
    """Generates a rank list of indices of the articles according to the specified favourites list
    
    Uses BeautifulSoup methods to find the favourites

    Parameters
    ----------
    articles : BeautifulSoup object
        all articles we want to search
    favourites : list of strings
        favourites we search for
    html_class : str
        defines html class we search in
    rank_list : list of int
        list that the favourites are appended to
    
    Returns
    -------
    rank_list : list of int
        list with appended favourites
    """
    for i,div in enumerate(articles):
        # filter that we use
        div_class = div.find("p", {'class': html_class})
        for favourite in favourites:
            if favourite.lower() in str(div_class).lower():
                rank_list.append(i)
    return rank_list


if date.today().weekday() == 0:  # today is Monday
    day = date.today() - timedelta(days=4)
else:  # every other day
    day = date.today() - timedelta(days=2)

#Get list of conferences from the website:
all_conferences = [Conference(page) for page in get_all_conference_pages()]


# Reorder articles according to favourite keyword lists

# get all articles
all_articles = soup.find_all("li", {'class': 'arxiv-result'})
current_first_article = all_articles[0]

# find articles in all articles with matching keyword from favourite list
ranking = []
ranking = find_favourite_papers(all_articles, favourite_authors, 'authors', ranking)
ranking = find_favourite_papers(all_articles, favourite_words, 'title is-5 mathjax', ranking)
ranking = find_favourite_papers(all_articles, favourite_words, 'abstract mathjax', ranking)

ranking = list(set(ranking)) # get rid of multiple entries
ranking.sort() # sort the entries

# shuffel the favourites to the top according to the ranking list
for i in ranking:
    if i != 0:
        current_first_article.insert_before(all_articles[i])
        current_first_article = all_articles[i]

# insert text that indicates the end of our suggested papers
all_articles = soup.find_all("li", {'class': 'arxiv-result'})
all_articles[len(ranking)].insert_before(BeautifulSoup('<h1 class="title"> <center> --- End Suggestion Section --- </center> </h1>', features='html.parser'))


#print(soup, 'html')

# Send email
SUBJECT = "Your daily arXiv update {}".format(date.today())
FROM = "Diamond-software-qutech@lists.tudelft.nl"

server = smtplib.SMTP('smtp.tudelft.nl')

for to in TO:
    msg = MIMEText(str(soup), 'html')
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = to

    try:
        server.sendmail(FROM, to, msg.as_string())
    except:
        print("Sending email to {} failed.".format(to))

server.quit()
