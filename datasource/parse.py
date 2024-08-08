from dataclasses import dataclass, asdict
import os
import json
import pickle
from functools import wraps
import sys
import time
from typing import Optional, List
from scholarly import scholarly
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm


def clean(s: str):
    # remove any non-letters in s
    return s

@dataclass
class Professor:
    first: str
    last: str
    middle: Optional[str]
    department: str
    website: str

    def name(self):
        m = self.middle+" " if self.middle else ""
        return f"{self.first} {m}{self.last}"

@dataclass
class Publication:
    author: Professor
    title: str
    abstract: str
    url: str
    pub_year: int


def get_gscholar_pubs(prof: Professor, limit=3):
    author_name = prof.name()
    authors = list(scholarly.search_author(author_name))
    authors = [author for author in authors
               if 'university of rochester' in author["affiliation"].lower()]
    if not authors:
        return []

    # take the first one
    author = authors[0]

    # Retrieve all the details for the author
    author = scholarly.fill(author)

    # Take a closer look at the first publication
    for pub in tqdm(author['publications'][:limit]):
        first_pub = scholarly.fill(pub)
        bib = pub["bib"]
        yield Publication(
            author=prof,
            title=bib.get('title', ""),
            abstract=bib.get('abstract', ""),
            url=pub.get("pub_url", "nourl"),
            pub_year=bib.get('pub_year', 1),
        )
        time.sleep(1.1)

deptmap = {
    "cs": "data/cs.html",
    "math": "data/math.html",
    "chem": "data/chem.html",
    "physics": "data/physics.html",
}

def dept(i):
    fi = deptmap[i]
    with open(fi) as f:
        return f.read()

def get_profs(department: str, limit=3):
    html = dept(department)
    soup = BeautifulSoup(html, "html.parser")

    links = [tag for tag in soup.find_all('h4', {"class": "name"})]
    for link in tqdm(links[:limit]):
        user = [group for group in link if group.name == 'a']
        if user:
            user = user[0]
        else:
            continue

        # TODO: there is a bug here for math dept (at least)
        (last, first) = user.contents[0].split(", ")
        t = first.split()
        if len(t) >= 2:
            first = clean(t[0])
            middle = clean(t[1])
        else:
            middle = ''
        
        p = Professor(
            first=first,
            last=last,
            middle=middle,
            department=department,
            website=user['href'],
        )
        yield p

def get_pubs(profs: List[Professor], dept: str, limit=None):
    t = str(int(time.time()))
    pubs = []
    for prof in profs:
        try:
            prof_pubs = list(get_gscholar_pubs(prof, limit=limit))
            pubs.extend([asdict(p) for p in prof_pubs])

            # write and checkpoint
            with open(f"parsed/checkpoint/{dept}_{t}.json", "w") as f:
                json.dump(list(pubs), f, indent=2)

        except Exception as e:
            print(f"failed to fetch pubs for professor '{prof.name()}'")
            print(e)

    # final write
    with open(f"parsed/{dept}_{t}.json", "w") as f:
        json.dump(list(pubs), f, indent=2)

    return pubs

def main(limit=None):
    if len(sys.argv) != 2 or sys.argv[1] not in deptmap.keys():
        print("bad usage")
        return

    dept = sys.argv[1]

    # get profs
    profs = get_profs(dept, limit=limit)

    # get pubs
    get_pubs(profs, dept, limit=limit)
    
if __name__ == "__main__":
    main()
