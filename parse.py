from bs4 import BeautifulSoup

import os
import pickle
import requests
from functools import wraps

def cache_get(func):
    @wraps(func)
    def wrapper(url, *args, **kwargs):
        filename = os.path.join('/tmp', url.replace('/', '_'))  # Creates unique filenames for each url

        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                print('Serving cached result for ' + url)
                return pickle.load(f)

        response = func(url, *args, **kwargs)

        with open(filename, 'wb') as f:
            pickle.dump(response, f)

        return response

    return wrapper

departments = [
    "https://www.cs.rochester.edu/people/faculty/index.html",
    "https://www.sas.rochester.edu/mth/people/faculty/index.html"
]

@cache_get
def _fetch(url):
    print('Fetching ' + url)
    return requests.get(url).text

deptmap = {
    "cs": "/Users/matt/Downloads/cs.html",
    "math": "/Users/matt/Downloads/math.html",
    "chem": "/Users/matt/Downloads/chem.html",
    "physics": "/Users/matt/Downloads/physics.html",
}

def dept(i):
    fi = deptmap[i]
    with open(fi) as f:
        return f.read()
import sys

if len(sys.argv) != 2 or sys.argv[1] not in deptmap.keys():
    print("bad usage")
    sys.exit()


html = dept(sys.argv[1])

soup = BeautifulSoup(html, "html.parser")

from dataclasses import dataclass
@dataclass
class Person:
    first: str
    last: str
    middle: str
    website: str
    gscholar: str

links = [tag for tag in soup.find_all('h4', {"class": "name"})]
for link in links:
    #print(link.contents)
    user = [group for group in link if group.name == 'a']
    if user:
        user = user[0]
    else:
        continue
    
    name = (user['href'], user.contents)
    print(name)
