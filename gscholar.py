import json
import sys
import time
from dataclasses import dataclass

from tqdm import tqdm
from scholarly import scholarly

p = lambda x : print(json.dumps(x, indent=2))

@dataclass
class Publication:
    author: str
    title: str
    abstract: str
    url: str
    pub_year: int


def get_pubs(author_name: str, limit=3):
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
        #p(pub)
        bib = pub["bib"]
        yield Publication(
            author=author_name,
            title=bib.get('title', ""),
            abstract=bib.get('abstract', ""),
            url=pub.get("pub_url", 1),
            pub_year=bib.get('pub_year', ""),
        )
        time.sleep(1)

def test():
    profs = [
        "John Criswell",
        "Chen Ding",
        "Sreepathi Pai",
        "Michael Scott",
    ]

    pubs = list(get_pubs(profs[0]))
    print(pubs)

if __name__ == "__main__":
    test()
