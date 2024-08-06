from dataclasses import dataclass, asdict
import os
import json
import pickle
from functools import wraps
import sys
import time
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
            prof_pubs = list(gscholar.get_pubs(prof, limit=limit))
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
    main(10)
