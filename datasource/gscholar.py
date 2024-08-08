import json
import sys
import time
from dataclasses import dataclass

from tqdm import tqdm
from scholarly import scholarly
from parse import Professor

p = lambda x : print(json.dumps(x, indent=2))


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
