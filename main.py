import os
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Any

import httpx
import pyvitals
from alive_progress import alive_bar
from colorama import Fore, Style, init


def make_download_folder(path: Path) -> None:
    if path.exists():
        print(Fore.YELLOW + Style.BRIGHT + f'Warning: folder "{path.absolute()}" already exists!')
        return

    path.mkdir()
    print(Fore.GREEN + Style.BRIGHT + f'Created folder "{path.absolute()}", saving levels there.')


def prompt_users() -> dict[str, Any]:
    output = {}

    # TODO: Prompt for download path

    # Prompt user for what levels to download
    while True:
        ask_checked = input("Would you like to download checked levels only? (Y/n) ").lower()

        if ask_checked in ['n', 'no']:
            output['verified_only'] = False
            break
        elif ask_checked in ['y', 'yes', '']:
            output['verified_only'] = True
            break
        else:
            print(Fore.RED + f'ERROR: "{ask_checked}" is not a valid option.')

    # Prompt user for number of download threads
    while True:
        threads = input("How many download threads would you like to use? (Default: 8) ")

        if not threads:
            output['threads'] = 8
            break

        try:
            output['threads'] = int(threads)
            if output['threads'] < 1:
                raise ValueError
        except ValueError:
            print(Fore.RED + f'ERROR: "{threads}" is not a positive integer.')
        else:
            break

    return output


def get_site_urls(verified_only: bool) -> list[str]:
    print(Fore.CYAN + "Accessing website...")

    with httpx.Client() as client:
        site_data = pyvitals.get_sheet_data(client, verified_only=verified_only)
    site_urls = [level['download_url'] for level in site_data]

    print(Fore.GREEN + f"Success! Total levels found: {len(site_urls)}\n")

    return site_urls


def main_download(path: Path, urls: list[str], threads: int) -> None:
    # use different settings for the progress bar as windows doesn't have the right fonts
    IS_WINDOWS = os.name == 'nt'
    bar = 'classic2' if IS_WINDOWS else 'smooth'
    spinner = 'classic' if IS_WINDOWS else 'notes_scrolling'

    with (httpx.Client() as client, ThreadPool(threads) as pool,
          alive_bar(len(urls), bar=bar, spinner=spinner) as bar):

        def download(url: str) -> None:
            try:
                result = pyvitals.download_level(client, url, path)
            except (pyvitals.BadRDZipFile, pyvitals.BadURLFilename):
                print(f"{url} failed to download correctly. Please contact a mod about this.")
            else:
                if IS_WINDOWS:
                    print(f"Downloaded {result.name:<80}")
                else:
                    print(Fore.GREEN + f"Downloaded {result}" + Fore.RESET)

        results = pool.imap_unordered(download, urls)
        for _ in results:
            bar()


def main() -> None:
    init(autoreset=True)  # Setup colorama for colored terminal text.

    DOWNLOAD_PATH = Path('.', 'downloader')

    make_download_folder(DOWNLOAD_PATH)
    config = prompt_users()
    site_urls = get_site_urls(config['verified_only'])
    main_download(DOWNLOAD_PATH, site_urls, config['threads'])

    input(Fore.GREEN + Style.BRIGHT + "Done downloading! Press Enter to continue...")


if __name__ == '__main__':
    main()
