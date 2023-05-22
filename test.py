from Conference_Hunting import get_all_conferences, Conference, ConferenceList

from rich import print as rprint
from tqdm import tqdm
from rich.console import Console
from rich.text import Text
import pickle

from datetime import timedelta

all_confs: ConferenceList = get_all_conferences(at_most_in_future=timedelta(days=40))



print("Total conferences in date range:", len(all_confs))
print("Latest Conference:", max(c.date for c in all_confs))

prog = tqdm(total=len(all_confs), desc="Finding Details")

c: Conference
for c in all_confs: #Gets details of conferences
    c.retrieve_details()
    prog.update()

with open("all_confs.pickle", 'wb') as F:
    pickle.dump(all_confs, F)

prog.close()
all_confs.match_keywords(number_of_keywords=12) #Filters all_confs down to only those conferences with at least (number_of_keywords) keywords





prog = tqdm(total=len(all_confs), desc="Finding Speakers")
for c in all_confs:
    c.retrieve_speakers() #Gets speakers of remaining conferences
    prog.update()

prog.close()
all_confs.match_speakers(number_of_speakers=0) #Filters all_confs down to only those conferences with at least (number_of_speakers) of given speakers on the Program Page
print()
print(f"Number of found Conferences: ({len(all_confs)})")
# rprint(all_confs.as_table(keywords=True, speakers=True, show_url=True), file=open("table.txt",'w'))
# # print("----")
#
# with open("table.txt", 'r') as F:
#     print(F.read())

console = Console(width=200)
with console.capture() as capture:
    console.print(all_confs.as_table(show_url=True, keywords=False, speakers=False))

print(Text.from_ansi(capture.get()))



