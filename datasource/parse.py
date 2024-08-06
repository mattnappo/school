from dataclasses import dataclass, asdict
import os
import json
import pickle
from functools import wraps
import sys
from typing import Optional, List

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

import gscholar

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
            pubs=None,
        )
        p.pubs = list(gscholar.get_pubs(p.name(), limit=limit))
        yield p

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in deptmap.keys():
        print("bad usage")
        return

    profs = []

    for prof in get_profs(sys.argv[1], limit=None):
        prof = asdict(prof)
        profs.append(prof)

        # write checkpoint
        with open("parsed/checkpoint.json", "w") as f:
            json.dump(profs, f, indent=2)

    with open("parsed/full.json", "w") as f:
        json.dump(profs, f, indent=2)
    
if __name__ == "__main__":
    main()
