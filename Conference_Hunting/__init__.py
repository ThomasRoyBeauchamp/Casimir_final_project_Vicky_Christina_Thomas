from bs4 import BeautifulSoup
import requests
import bs4

from key_words import key_words as KEYWORDS
from key_words import key_authors as SPEAKERS

from datetime import date, timedelta

CONFERENCE_INDEX_URL: str = "https://conferenceindex.org/conferences/quantum-physics"

MONTH_DICT = {
    "JANUARY": 1,
    "FEBRUARY": 2,
    "MARCH": 3,
    "APRIL": 4,
    "MAY": 5,
    "JUNE": 6,
    "JULY": 7,
    "AUGUST": 8,
    "SEPTEMBER": 9,
    "OCTOBER": 10,
    "NOVEMBER": 11,
    "DECEMBER": 12
}

def get_conferences_from_webpage(raw_html):

    website = BeautifulSoup(raw_html, "html.parser")

    website.find("header").decompose()
    website.find("footer").decompose()

    eventList = website.find("div", {"id": "eventList"})

    conference_entries = [x for y in eventList.find_all("ul", {"class":"list-unstyled"}) for x in y.find_all("li")]

    year_mapping = dict([tuple(x.strong.text.split(',')) for x in eventList.find_all("div", {"class": "card-header"})])

    for k in year_mapping.keys():
        year_mapping[k] = int(year_mapping[k])


    return [Conference(d, year_mapping) for d in conference_entries]


def get_all_conference_pages():

    pages = []
    go_to_next_page = True
    page = 1
    while go_to_next_page:
        try:
            http_request = requests.get(CONFERENCE_INDEX_URL + f'?page={page}')
        except:
            break

        if http_request.status_code == 200:

            new_conference_pages = get_conferences_from_webpage(http_request.content)

            if new_conference_pages:
                pages += new_conference_pages ##adds the new conferences to the list of all conferences
            else:
                go_to_next_page = False
        else:
            break

        page += 1

    return pages

def do_html_request(website: str) -> (bool, BeautifulSoup | None):
    """
    Handles the HTTP request.
    :param website: Website to retrieve
    :return: (Successful, Website as BeautifulSoup or None)
    """
    try:
        html_request = requests.get(website)

        if html_request.status_code == 200:
            return True, BeautifulSoup(html_request.content)
        else:
            return False, None

    except:

        return False, None

class Conference:

    def __init__(self, div: bs4.Tag, year_mapping: dict):

        _text = div.text.split("\n")
        while '' in _text:
            _text.remove('')

        self.name = _text[1].lstrip()

        self.location = _text[2].lstrip().replace("- ", "")

        _date = _text[0].lstrip().split(' ')
        self.date = date(year=year_mapping[_date[0]], month=MONTH_DICT[_date[0].upper()], day=int(_date[1]))

        self.website = div.a.attrs["href"]

        pass

    # def __init__(self, webpage):
    #
    #     self.did_load = False
    #
    #     website = BeautifulSoup(requests.get(webpage).content, 'html.parser')
    #
    #     website.find("header").decompose()
    #     website.find("footer").decompose()
    #
    #     a: bs4.NavigableString
    #
    #     _desc = website.find("div", {"id": "event-description"}) ##Finds the event description tag
    #     if _desc is not None:
    #         for b in _desc.find_all("br"):  ##Converts <br> tags to \n
    #             b.replaceWith(" | ")
    #
    #         self.description = _desc.text.lower()
    #             # .split('\n')  # Converts contents to lower case
    #         # if '' in self.description:
    #         #     self.description.remove('')
    #         # self.description[0] = self.description[0].lstrip()
    #
    #     else:
    #         self.description = []
    #
    #
    #     self.title = website.find("div", {"class": "col-lg-9 col-sm-12"}).find("h1").text
    #
    #
    #
    #     self.tags = ' | '.join([a.text for a in website.find("li", {"class": "mt-3"}).find_all('a')]) ##tags contained in a li tag with class mt-3
    #
    #     details_container = website.find("ul", {"class": "mb-2 list-unstyled"})
    #
    #     lines = details_container.find_all("li")
    #
    #     self.attrs = dict([tuple(l.text.split(":", 1)) for l in lines if "class" not in l.attrs.keys()])
    #     ## Contains everything in the Shortname, type, URLs etc.
    #
    #     if "Date" in self.attrs.keys():
    #
    #         _date = self.attrs["Date"].split(" ")
    #
    #         self.date = date(day=int(_date[2].split('-')[0]) if '-' in _date[2] else int(_date[2]), month=MONTH_DICT[_date[1].upper()], year = int(_date[3]))
    #
    #     else:
    #         self.date = date(year=0, month=0, day=0)
    #
    #     if not (date.today() + timedelta(days=60) < self.date < date.today() + timedelta(days=6*30)):
    #         return
    #
    #
    #     self._keywords = [kwd for kwd in KEYWORDS if kwd in self.tags or kwd in self.description]
    #
    #
    #
    #     if "Program URL" in self.attrs.keys() and self._keywords: #Only looks for speakers if there are keywords
    #         program_page = BeautifulSoup(requests.get(self.attrs["Program URL"]).content, 'html.parser').text
    #
    #         self._speakers = [spk for spk in SPEAKERS if spk in program_page]
    #     else:
    #         self._speakers = []
    #
    #
    #     self.did_load = True



    @property
    def speakers(self):
        return self._speakers


    @property
    def keywords(self):

        return self._keywords

    def __eq__(self, other):
        return self.title == other.title

