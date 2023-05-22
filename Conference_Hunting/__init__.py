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
    "DECEMBER": 12,
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}

SHORT_LONG_MONTHS = {
    "Jan": "January",
    "Feb": "February",
    "Mar": "March",
    "Apr": "April",
    "May": "May",
    "Jun": "June",
    "Jul": "July",
    "Aug": "August",
    "Sep": "September",
    "Oct": "October",
    "Nov": "Novemeber",
    "Dec": "December"

}

def get_conferences_from_webpage(website: BeautifulSoup, at_least_in_future: timedelta = timedelta(days=30), at_most_in_future: timedelta = timedelta(days=180)):
    """

    :param website: Website to look for conferences on
    :param at_least_in_future: (opt: 30 days) Minimum time until the start of the conference
    :param at_most_in_future: (opt: 180 days) Maximum time until the start of the conference
    :return: List of Conference class objects in the date range.
    """

    # website = BeautifulSoup(raw_html, "html.parser")

    website.find("header").decompose()
    website.find("footer").decompose()

    eventList = website.find("div", {"id": "eventList"})

    conference_entries = [x for y in eventList.find_all("ul", {"class":"list-unstyled"}) for x in y.find_all("li")]

    year_mapping = dict([tuple(x.strong.text.split(',')) for x in eventList.find_all("div", {"class": "card-header"})])

    for k in year_mapping.keys():
        year_mapping[k] = int(year_mapping[k])

    all_conferences = [Conference(d, year_mapping) for d in conference_entries]

    go_later = date.today() + at_least_in_future > min(c.date for c in all_conferences)

    return go_later, ConferenceList([c for c in all_conferences if date.today() + at_least_in_future <= c.date <= date.today() + at_most_in_future])



def get_all_conferences():

    conferences = ConferenceList()
    go_to_next_page = True
    page = 1
    while go_to_next_page:

        got_page, website = do_html_request(CONFERENCE_INDEX_URL + f'?page={page}')

        if got_page:
            go_to_next_page, new_conferences = get_conferences_from_webpage(website)

            conferences += new_conferences

        else:
            break

        page += 1

    return conferences

def do_html_request(website: str) -> (bool, BeautifulSoup | None):
    """
    Handles the HTTP request.
    :param website: Website to retrieve
    :return: (Successful, Website as BeautifulSoup or None)
    """
    try:
        html_request = requests.get(website)

        if html_request.status_code == 200:
            return True, BeautifulSoup(html_request.content, "html.parser")
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
        self.date = date(year=year_mapping[SHORT_LONG_MONTHS[_date[0]]], #Looks up the year after converting from e.g. Jan to January
                         month=MONTH_DICT[_date[0].upper()], #Looks up numberical month
                         day=int(_date[1]))

        self.website = div.a.attrs["href"]

        self._keywords: str = ''
        self._description: str = ''
        self._tags: str = ''
        self._attrs: dict = dict()
        self._speakers: list = list()

        pass



    # def __init__(self, webpage):
    #
    #     self.did_load = False
    #
    #     website = BeautifulSoup(requests.get(webpage).content, 'html.parser')
    #
    #
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

    @property
    def atributes(self):
        return self._attrs

    def retrieve_details(self):
        got_page, website = do_html_request(self.website)
        if got_page:
            website.find("header").decompose()
            website.find("footer").decompose()

            a: bs4.NavigableString

            _desc = website.find("div", {"id": "event-description"}) ##Finds the event description tag

            if _desc is not None:
                for b in _desc.find_all("br"):  ##Converts <br> tags to \n
                    b.replaceWith(" | ")

                self._description = _desc.text.lower()
            else:
                self._description = ''

            self._tags = ' | '.join([a.text for a in website.find("li", {"class": "mt-3"}).find_all('a')]) ##tags contained in a <li> tag with class mt-3

            details_container = website.find("ul", {"class": "mb-2 list-unstyled"})

            lines = details_container.find_all("li")

            self._attrs = dict([tuple(l.text.split(":", 1)) for l in lines if "class" not in l.attrs.keys()])

            self._keywords = [kwd for kwd in KEYWORDS if kwd in self._tags or kwd in self._description]

    def retrieve_speakers(self, retrieve_details: bool = False):
        if "Program URL" in self._attrs.keys():
            got_page, program_page = do_html_request(self._attrs["Program URL"])
            if got_page:
                self._speakers = [spk for spk in SPEAKERS if spk in program_page]

        else:
            if retrieve_details:
                self.retrieve_details()
                self.retrieve_speakers()

    def __eq__(self, other):
        return self.name == other.name


class ConferenceList(list):

    def __init__(self, __iterable=None):
        if __iterable is None:
            __iterable = list()
        super().__init__(__iterable)
        self.sort()  ##Sorts the list by date order

    def append(self, __object: Conference) -> None:
        super().append(__object)
        self.sort()

    def sort(self, *, key: None = lambda x: x.date, reverse: bool = False) -> None: ##Sorts the list by date order by default
        super().sort(key=key, reverse=reverse)

    def match_keywords(self, number_of_keywords: int = 5):
        c: Conference
        _non_matching = [c for c in self if len(c.keywords) < number_of_keywords]
        for c in _non_matching:
            self.remove(c)

    def match_speakers(self, number_of_speakers: int = 0):
        c: Conference
        _non_matching = [c for c in self if len(c.speakers) < number_of_speakers]
        for c in _non_matching:
            self.remove(c)

    def __str__(self):
        c: Conference
        return "\n".join([f"{c.name} - {c.date} - {c.location}" for c in self])
