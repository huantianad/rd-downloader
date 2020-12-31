import os
import re
from multiprocessing.pool import ThreadPool

import requests
from clint.textui import progress

levelpath = "downloader"


# Print color definitions
def prGreen(skk): print(f"\033[32m{skk}\033[00m")
def prCyan(skk): print(f"\033[36m{skk}\033[00m")
def prOrange(skk): print(f"\033[33m{skk}\033[00m")
def prRed(skk): print(f"\033[31m{skk}\033[00m")


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


# Checks if the level given is verified
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
    prGreen("Success!")

    # Allow user to decide whether to download checked or all levels
    while True:
        ask_checked = input("Would you like to download (a)ll or (c)hecked levels? ")
        if ask_checked.lower() in ['a', 'all']:
            site_urls = [x['download_url'] for x in site_data]
            prCyan("Downloading all levels...")
            break
        elif ask_checked.lower() in ['c', 'checked']:
            site_urls = [x['download_url'] for x in site_data if check_verified(x)]
            prCyan("Downloading checked levels...")
            break
        else:
            prRed(f"ERROR: \"{ask_checked}\" is not a valid option.")

    prCyan(f"Total levels found: {len(site_urls)}\n")

    results = ThreadPool(8).imap_unordered(download, site_urls)
    for chunk in progress.bar(results, expected_size=len(site_urls)):
        prGreen(f"Downloaded {chunk}" + ' ' * 30)

    input("Done downloading! Press Enter to continue...")


if __name__ == '__main__':
    main()
