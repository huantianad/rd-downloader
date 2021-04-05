import os
import re
from multiprocessing.pool import ThreadPool

from alive_progress import alive_bar
import requests


level_path = "downloader"


# Print color definitions
def pr_green(skk): print(f"\033[32m{skk}\033[00m")
def pr_cyan(skk): print(f"\033[36m{skk}\033[00m")
def pr_orange(skk): print(f"\033[33m{skk}\033[00m")
def pr_red(skk): print(f"\033[31m{skk}\033[00m")


def rename(path: str):
    if os.path.exists(path):
        index = 1
        path = path.replace(".rdzip", "")  # Gets rid of the .rdzip extension, we add it back later on.
        while os.path.exists(f"{path} ({index}).rdzip"):
            index += 1
        return f"{path} ({index}).rdzip"
    else:
        # When the file doesn't exist, we don't need to do anything, so we can just directly return the filename
        return path


def get_url_filename(url: str) -> str:
    if url.endswith('.rdzip'):
        # When the filename already ends with the file extension, we can just snatch it from the url
        name = url.split('/')[-1]
    else:
        # Otherwise, we need to use some weird stuff to get it from the Content-Disposition header
        r = requests.get(url).headers.get('Content-Disposition')
        name = re.findall('filename=(.+)', r)[0].split(";")[0].replace('"', "")

    # Remove the characters that windows doesn't like in filenames
    for char in r'<>:"/\|?* ':
        name = name.replace(char, '')

    return name


def download_level(url: str):
    # Get the proper filename of the level, append it to the path to get the full path to the downloaded level.
    filename = get_url_filename(url)
    full_path = os.path.join(level_path, filename)

    # Get a unique file name
    full_path = rename(full_path)

    # Download the level
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(full_path, 'wb') as file:
            for chunk in r:
                file.write(chunk)
    else:
        pr_red(f'''ERROR: Status code not 200 when downloading {full_path}, maybe the level was deleted on discord?
               Please tell a mod about this. level url: {url}''')

    return full_path  # Returns the final path to the downloaded level


def main():
    if not os.path.exists(f'{level_path}/'):
        os.mkdir(f'{level_path}/')
        pr_green(f'Created folder {level_path}, saving levels there.')
    else:
        pr_red(f'ERROR: folder "{level_path}" already exists! Please remove and try again.')
        return

    pr_cyan("Accessing website...")
    url = 'https://script.google.com/macros/s/AKfycbzm3I9ENulE7uOmze53cyDuj7Igi7fmGiQ6w045fCRxs_sK3D4/exec'
    site_data = requests.get(url).json()
    pr_green("Success!")

    # Prompt user for what levels to download
    while True:
        ask_checked = input("Would you like to download (a)ll or (c)hecked levels? ")
        if ask_checked.lower() in ['a', 'all']:
            site_urls = [x['download_url'] for x in site_data]
            pr_cyan("Downloading all levels...")
            break
        elif ask_checked.lower() in ['c', 'checked']:
            site_urls = [x['download_url'] for x in site_data if x.get('verified')]
            pr_cyan("Downloading checked levels...")
            break
        else:
            pr_red(f'ERROR: "{ask_checked}" is not a valid option.')

    pr_cyan(f"Total levels found: {len(site_urls)}\n")

    results = ThreadPool(8).imap_unordered(download_level, site_urls)
    with alive_bar(len(site_urls), spinner='notes_scrolling') as bar:
        for result in results:
            pr_green(f"Downloaded {result}")
            bar()

    input("Done downloading! Press Enter to continue...")


if __name__ == '__main__':
    main()
