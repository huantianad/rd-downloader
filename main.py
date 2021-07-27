import os
import re
from multiprocessing.pool import ThreadPool

import colorama
import requests
from alive_progress import alive_bar
from termcolor import cprint


def rename(path: str) -> str:
    if os.path.exists(path):
        index = 2
        extension = '.' + path.rsplit('.', 1)[-1]
        path = path.replace(extension, '')  # Gets rid of the .rdzip extension, we add it back later on.

        while os.path.exists(f"{path} ({index}){extension}"):
            index += 1

        return f"{path} ({index}){extension}"
    else:
        return path


def get_url_filename(url: str) -> str:
    if url.endswith('.rdzip'):
        # When the filename already ends with the file extension, we can just snatch it from the url
        name = url.split('/')[-1]
    else:
        # Otherwise, we need to use some weird stuff to get it from the Content-Disposition header
        r = requests.get(url, allow_redirects=True, stream=True)
        h = r.headers.get('Content-Disposition')
        name = re.findall(r'filename="(.+)"', h)[0]

    # Remove the characters that windows doesn't like in filenames
    for char in r'<>:"/\|?*':
        name = name.replace(char, '')

    return name


def download_level(url: str):
    # Get the proper filename of the level, append it to the path to get the full path to the downloaded level.
    filename = get_url_filename(url)
    full_path = os.path.join(DOWNLOAD_PATH, filename)

    # Get a unique file name
    full_path = rename(full_path)

    # Download the level
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(full_path, 'wb') as file:
            for chunk in r:
                file.write(chunk)
    else:
        if IS_WINDOWS:
            print(f'''ERROR: Status code not 200 when downloading {full_path}, maybe the level was deleted on discord?
                   Please tell a mod about this. level url: {url}''')
        else:
            cprint(f'''ERROR: Status code not 200 when downloading {full_path}, maybe the level was deleted on discord?
                   Please tell a mod about this. level url: {url}''', 'red')

    return full_path  # Returns the final path to the downloaded level


def main():
    global DOWNLOAD_PATH
    global IS_WINDOWS
    DOWNLOAD_PATH = "downloader/"
    IS_WINDOWS = os.name == 'nt'

    # windows is dumb, color fixes
    colorama.init()

    if not os.path.exists(DOWNLOAD_PATH):
        os.mkdir(DOWNLOAD_PATH)
        cprint(f'Created folder {os.path.abspath(DOWNLOAD_PATH)}, saving levels there.', 'green')
    else:
        cprint(f'Warning: folder "{os.path.abspath(DOWNLOAD_PATH)}" already exists!', 'yellow')

    cprint("Accessing website...", 'cyan')
    url = 'https://script.google.com/macros/s/AKfycbzm3I9ENulE7uOmze53cyDuj7Igi7fmGiQ6w045fCRxs_sK3D4/exec'
    site_data = requests.get(url).json()
    cprint("Success!", 'green')

    # Prompt user for number of download threads
    while True:
        threads = input("How many download threads would you like to use? (Default: 8) ")

        if not threads:
            threads = 8
            break

        try:
            threads = int(threads)
        except ValueError:
            cprint(f'ERROR: "{threads}" is not a valid integer!')
        else:
            break

    # Prompt user for what levels to download
    while True:
        ask_checked = input("Would you like to download checked levels only? (Y/n) ")
        if ask_checked.lower() in ['n', 'no']:
            site_urls = [x['download_url'] for x in site_data]
            cprint("Downloading all levels...", 'cyan')
            break
        elif ask_checked.lower() in ['y', 'yes', '']:
            site_urls = [x['download_url'] for x in site_data if x.get('verified')]
            cprint("Downloading checked levels...", 'cyan')
            break
        else:
            cprint(f'ERROR: "{ask_checked}" is not a valid option.', 'red')

    cprint(f"Total levels found: {len(site_urls)}\n", 'cyan')

    # use different settings for the progress bar as windows doesn't have the right fonts
    bar = 'classic2' if IS_WINDOWS else 'smooth'
    spinner = 'classic' if IS_WINDOWS else 'notes_scrolling'

    results = ThreadPool(threads).imap_unordered(download_level, site_urls)
    with alive_bar(len(site_urls), bar=bar, spinner=spinner) as bar:
        for result in results:
            if IS_WINDOWS:
                print(f"Downloaded {result.ljust(76)}")
            else:
                cprint(f"Downloaded {result}", 'green')
            bar()

    input("Done downloading! Press Enter to continue...")


if __name__ == '__main__':
    main()
