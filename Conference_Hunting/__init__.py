from bs4 import BeautifulSoup
import requests
import bs4

CONFERENCE_INDEX_URL: str = "https://conferenceindex.org/conferences/quantum-physics"

def get_conference_pages(raw_html):

    website = BeautifulSoup(raw_html, "html.parser")

    website.find("header").decompose()
    website.find("footer").decompose()

    eventList = website.find("div", {"id": "eventList"})

    try:
        return [c.attrs["href"] for c in eventList.find_all("a") if "title" in c.attrs.keys()]
    except:
        return []

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

            new_conference_pages = get_conference_pages(http_request.content)
            if len(new_conference_pages) > 0:
                pages += new_conference_pages ##adds the new conferences to the list of all conferences
            else:
                go_to_next_page = False
        else:
            break

        page += 1

    return pages



class Conference:

    def __init__(self, webpage):

        website = BeautifulSoup(requests.get(webpage).content, 'html.parser')

        website.find("header").decompose()
        website.find("footer").decompose()

        a: bs4.NavigableString

        _desc = website.find("div", {"id": "event-description"}) ##Finds the event description tag
        for b in _desc.find_all("br"):  ##Converts <br> tags to \n
            b.replaceWith("\n")

        self.title = website.find("div", {"class": "col-lg-9 col-sm-12"}).find("h1").text

        self.description = _desc.text.lower().split('\n') #Converts contents to lower case
        if '' in self.description:
            self.description.remove('')
        self.description[0] = self.description[0].lstrip()

        self.tags = [a.text for a in website.find("li", {"class": "mt-3"}).find_all('a')] ##tags contained in a li tag with class mt-3

        details_container = website.find("ul", {"class": "mb-2 list-unstyled"})

        lines = details_container.find_all("li")

        self.attrs = dict([tuple(l.text.split(":", 1)) for l in lines if "class" not in l.attrs.keys()])


    def get_speakers(self, speaker_list:[str]) -> list[str]:

        program_page = BeautifulSoup(requests.get(self.attrs["Program URL"]).content, 'html.parser').text

        return [spk for spk in speaker_list if spk in program_page]


