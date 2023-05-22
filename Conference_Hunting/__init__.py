from bs4 import BeautifulSoup
import requests
import bs4

from key_words import key_words as KEYWORDS
from key_words import key_authors as SPEAKERS

from datetime import date, timedelta

from rich.table import Table

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
    "Nov": "November",
    "Dec": "December"

}

class Conference:
    """
    Class to hold information about conferences. It has 3 properties:
        self.speakers: List of known speakers from SPEAKERS at the conference
        self.keywords:  List of keywords in KEYWORDS on the conference page
        self.attributes: Important information about the conference.

    These are populated with the functions self.retrieve_details for keywords and attributes, and self.retrieve_speakers for speakers.

    __eq__ is also redefined to have equality iff two conferences share the same name.

    The class is initialised using the <li> tag from the list in CONFERENCE_INDEX_URL
    """

    def __init__(self, div: bs4.Tag, year_mapping: dict):

        _text = div.text.split("\n")
        while '' in _text:
            _text.remove('')

        self.name = _text[1].lstrip()

        self.location = _text[2].lstrip().replace("- ", "")

        _date = _text[0].lstrip().split(' ')
        self.date = date(year=year_mapping[SHORT_LONG_MONTHS[_date[0]]],  # Looks up the year after converting from e.g. Jan to January
                         month=MONTH_DICT[_date[0].upper()],  # Looks up numerical month
                         day=int(_date[1]))

        self.website = div.a.attrs["href"]

        self._keywords: str = ''
        self._description: str = ''
        self._tags: str = ''
        self._attrs: dict = dict()
        self._speakers: list = list()

        pass


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

            _desc = website.find("div", {"id": "event-description"})  # Finds the event description tag

            if _desc is not None:
                for b in _desc.find_all("br"):  # Converts <br> tags to \n
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
    """
    Modified list class to force sorting by date order of conferences.

    Modified __str__ to return all entries in line-separated list in the format DATE NAME - LOCATION
    """

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
        return "\n".join([f"{c.date.strftime('%d/%m/%Y')} {c.name} - {c.location}" for c in self])

    def as_table(self, keywords: bool = False, speakers: bool = False):
        c: Conference

        table: Table = Table(title=f"Relevant Conferences ({len(self)})", show_lines=True)

        table.add_column("Date", justify="centre")
        table.add_column("Name", justify="centre")
        table.add_column("Location", justify="centre")
        if keywords:
            table.add_column("Keywords", justify="centre", no_wrap=False)
        if speakers:
            table.add_column("Speakers", justify="centre", no_wrap=False)

        for c in self:
            table.add_row(*[c.date.strftime('%d/%m/%Y'), c.name, c.location] + ([', '.join(c.keywords)] if keywords else []) + ([" ".join(c.speakers) if "Program URL" in c.atributes.keys() else 'N/A'] if speakers else []))

        return table



def get_conferences_from_webpage(website: BeautifulSoup, at_least_in_future: timedelta = timedelta(days=30), at_most_in_future: timedelta = timedelta(days=180)):
    """

    :param website: BeautifulSoup of website to look for conferences on
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

    go_later = date.today() + at_least_in_future > min(c.date for c in all_conferences)  # Checks if it found conferences later than the earliest permitted date

    return go_later, ConferenceList([c for c in all_conferences if date.today() + at_least_in_future <= c.date <= date.today() + at_most_in_future])



def get_all_conferences(website: str = None, at_least_in_future: timedelta = timedelta(days=30), at_most_in_future: timedelta = timedelta(days=180)):
    """

    :param website: (opt: None) Website to get data from. Defaults to https://conferenceindex.org/conferences/quantum-physics if no site supplied.
    :param at_least_in_future: (opt: default 30 days) Minimum time until the start of the conference
    :param at_most_in_future: (opt: default 180 days) Maximum time until the start of the conference
    :return: ConferenceList of all found conferences in date range.
    """

    conferences = ConferenceList()
    go_to_next_page = True
    page = 1
    while go_to_next_page:

        got_page, website = do_html_request((CONFERENCE_INDEX_URL if type(website) is not str else website) + f'?page={page}')

        if got_page:
            go_later, new_conferences = get_conferences_from_webpage(website, at_least_in_future=at_least_in_future,at_most_in_future=at_most_in_future)  # Get conferences on that page, passing through date parameters

            conferences += new_conferences

        else:
            break

        go_to_next_page = go_later or new_conferences  # Continues if we need to go further into the future, or it found new conferences on the current page

        page += 1
        # print(page)

    return conferences

def do_html_request(website: str) -> (bool, BeautifulSoup | None):
    """
    Handles the HTTP request.
    :param website: Website to retrieve
    :return: (Successful, Website as BeautifulSoup or None)
    """
    try:
        html_request = requests.get(website)

        if html_request.status_code == 200:  # Check we got a good response (HTTP code 200)
            return True, BeautifulSoup(html_request.content, "html.parser")
        else:
            return False, None

    except requests.RequestException:  # If we get any request related error back from requests.get.

        return False, None

