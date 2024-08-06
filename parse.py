from dataclasses import dataclass
import os
import pickle
from functools import wraps
import sys
from typing import Optional, List

from bs4 import BeautifulSoup
import requests

import gscholar

def clean(s: str):
    # remove any non-letters in s
    return s

@dataclass
class Professor:
    first: str
    last: str
    middle: Optional[str]
    website: str
    pubs: List[gscholar.Publication]

    def name(self):
        m = self.middle+" " if self.middle else ""
        return f"{self.first} {m}{self.last}"

departments = [
    "https://www.cs.rochester.edu/people/faculty/index.html",
    "https://www.sas.rochester.edu/mth/people/faculty/index.html"
]

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

def get_profs(department: str):
    html = dept(department)
    soup = BeautifulSoup(html, "html.parser")

    links = [tag for tag in soup.find_all('h4', {"class": "name"})]
    for link in links:
        user = [group for group in link if group.name == 'a']
        if user:
            user = user[0]
        else:
            continue

        (last, first) = user.contents[0].split(", ")
        t = first.split()
        if len(t) >= 2:
            first = clean(t[0])
            middle = clean(t[1])
        else:
            middle = None
        
        p = Professor(
            first=first,
            last=last,
            middle=middle,
            website=user['href'],
            pubs=None,
        )
        p.pubs = gscholar.get_pubs(p.name())
        yield p

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in deptmap.keys():
        print("bad usage")
        return

    profs = list(get_profs(sys.argv[1]))
    for prof in profs:
        print(prof)

    print(list(profs[13].pubs))

if __name__ == "__main__":
    main()
