import multiprocessing.pool as mpool
import re
from time import sleep

import requests
from requests.exceptions import ConnectionError

# gen urls
letters = 'abcdefghijklmnopqrstuvwxyz'
urls = []
for i in letters:
    for j in letters:
        for k in letters:
            code = i+j+k
            urls.append(f"https://www.sas.rochester.edu/{code}")

# do one url
def worker(url):
    res = requests.get(url)
    if res.status_code != 200:
        print(f"[FAIL] {url}")
        return
    print(f"[PASS] {url}")

    title = re.search("<title>(.*)</title>", res.text).group(1)
    print(title)

# do all urls
# pool = mpool.ThreadPool(2)
for url in urls:
    # pool.apply_async(worker, args=(url, ))
    try:
        worker(url)
        sleep(5)
    except ConnectionError:
        print("failed")
        sleep(2)

