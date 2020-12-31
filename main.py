import os
import re
from multiprocessing.pool import ThreadPool

import requests
from clint.textui import progress

levelpath = "downloader"


# Print color definitions
def prGreen(skk): print(f"\033[32m {skk}\033[00m")
def prCyan(skk): print(f"\033[36m {skk}\033[00m")
def prOrange(skk): print(f"\033[33m {skk}\033[00m")


# Iterate through possible renames until valid name
def rename(name, index):
    name = name.split('.rdzip')[0]
    if os.path.exists(f'{levelpath}/{name} ({index}).rdzip'):
        return rename(name, index + 1)
    else:
        return f"{name} ({index})" + ".rdzip"


def download(url):
    if url.startswith('https://drive.google.com/'):
        name = url.split('id=')[-1] + ".rdzip"
    elif url.startswith("https://www.dropbox.com/s/"):
        r = requests.get(url)
        name = re.findall('filename=(.+)', r.headers.get('Content-Disposition'))[0].split(";")[0].replace('"', "")
    else:
        name = url.split('/')[-1]

    if os.path.exists(f'{levelpath}/{name}'):
        name = rename(name, 1)

    r = requests.get(url, stream=True)
    with open(f'{levelpath}/{name}', 'wb') as f:
        for ch in r:
            f.write(ch)

    return name


def check_verified(level):
    try:
        return level['verified']
    except KeyError:
        return False


def main():
    if not os.path.exists(f'{levelpath}/'):
        os.mkdir(f'{levelpath}/')
        prOrange("Created download folder.")

    prCyan("Accessing website.")
    url = 'https://script.google.com/macros/s/AKfycbzm3I9ENulE7uOmze53cyDuj7Igi7fmGiQ6w045fCRxs_sK3D4/exec'
    site_data = requests.get(url).json()
    site_urls = [x['download_url'] for x in site_data]
    # site_urls = [x['download_url'] for x in site_data if check_verified(x)]

    prCyan(f"Total levels found: {len(site_urls)}\n")

    results = ThreadPool(8).imap_unordered(download, site_urls)
    for chunk in progress.bar(results, expected_size=len(site_urls)):
        prGreen(f"Done downloading {chunk}" + ' ' * 30)

    input("Done downloading! Press Enter to continue...")


if __name__ == '__main__':
    main()
