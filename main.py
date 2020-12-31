import os
import re
from multiprocessing.pool import ThreadPool

import requests
from clint.textui import progress

level_path = "downloader"


# Print color definitions
def pr_green(skk): print(f"\033[32m{skk}\033[00m")
def pr_cyan(skk): print(f"\033[36m{skk}\033[00m")
def pr_orange(skk): print(f"\033[33m{skk}\033[00m")
def pr_red(skk): print(f"\033[31m{skk}\033[00m")


# Iterate through possible renames until valid name
def rename(name, index):
    name = name.split('.rdzip')[0]
    if os.path.exists(f'{level_path}/{name} ({index}).rdzip'):
        return rename(name, index + 1)
    else:
        return f"{name} ({index})" + ".rdzip"


def download(url):
    if url.startswith('https://drive.google.com/') or url.startswith("https://www.dropbox.com/s/"):
        r = requests.get(url)
        name = re.findall('filename=(.+)', r.headers.get('Content-Disposition'))[0].split(";")[0].replace('"', "")
    else:
        name = url.split('/')[-1]

    if os.path.exists(f'{level_path}/{name}'):
        name = rename(name, 1)

    r = requests.get(url, stream=True)
    with open(f'{level_path}/{name}', 'wb') as f:
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
    if not os.path.exists(f'{level_path}/'):
        os.mkdir(f'{level_path}/')
        pr_orange("Created download folder.")

    pr_cyan("Accessing website.")
    url = 'https://script.google.com/macros/s/AKfycbzm3I9ENulE7uOmze53cyDuj7Igi7fmGiQ6w045fCRxs_sK3D4/exec'
    site_data = requests.get(url).json()
    pr_green("Success!")

    # Allow user to decide whether to download checked or all levels
    while True:
        ask_checked = input("Would you like to download (a)ll or (c)hecked levels? ")
        if ask_checked.lower() in ['a', 'all']:
            site_urls = [x['download_url'] for x in site_data]
            pr_cyan("Downloading all levels...")
            break
        elif ask_checked.lower() in ['c', 'checked']:
            site_urls = [x['download_url'] for x in site_data if check_verified(x)]
            pr_cyan("Downloading checked levels...")
            break
        else:
            pr_red(f"ERROR: \"{ask_checked}\" is not a valid option.")

    pr_cyan(f"Total levels found: {len(site_urls)}\n")

    results = ThreadPool(8).imap_unordered(download, site_urls)
    for chunk in progress.bar(results, expected_size=len(site_urls)):
        pr_green(f"Downloaded {chunk}" + ' ' * 30)

    input("Done downloading! Press Enter to continue...")


if __name__ == '__main__':
    main()
