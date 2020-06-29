import configparser
import json
import os
from multiprocessing.pool import ThreadPool

import requests
from clint.textui import progress


# Config stuff
config = configparser.ConfigParser()
config.read('config.ini')

if config.get('MAIN', 'Path'):
    levelpath = config.get('MAIN', 'Path')
else:
    levelpath = os.path.join('C:\\', 'Users', os.getlogin(), 'Documents', 'Rhythm Doctor', 'Levels')

samename = config.get('MAIN', 'OnSameName')
if not (samename == "overwrite" or samename == "rename" or samename == "skip"):
    raise ValueError("Invalid argument for OnSameName in config.ini")

dlmethod = config.get('MAIN', 'DownloadMethod')
if not (dlmethod == "position" or dlmethod == "difference"):
    raise ValueError("Invalid argument for DownloadMethod in config.ini")

threads = int(config.get('MAIN', 'ThreadNo'))
if threads <= 0:
    raise ValueError("Invalid argument for ThreadNo in config.ini")


# Create function to handle renaming.
def rename(name, index):
    if os.path.exists(f'{levelpath}/{name} ({index})'):
        return rename(name, index + 1)
    else:
        newname = name.split('.rdzip')[0]
        return f"{newname} ({index})" + ".rdzip"


# Download list of files from thing.
thing = requests.get(
    'https://script.google.com/macros/s/AKfycbzm3I9ENulE7uOmze53cyDuj7Igi7fmGiQ6w045fCRxs_sK3D4/exec').content
stuff = json.loads(thing.decode('utf-8'))
urls = []

print("Total number of levels: " + str(len(stuff)) + "\n")


if dlmethod == "position":
    # Prompt user for start and stop of levels to download
    start = int(input("Level to start at (index starts at 0): "))
    end = int(input("Level to end at (non-inclusive): "))

    if end - start == 1:
        print("Looping through 1 level.")
    else:
        print("Looping through " + str(end - start) + " levels.")
    print("\n")

    for level in stuff[start:end]:
        urls.append(level['download_url'])

if dlmethod == "difference":
    # Use data.txt to keep track of levels downloaded
    # Put urls of levels into urls list
    for level in stuff:
        urls.append(level['download_url'])

    # Read data.txt, compare to urls
    with open('data.txt', 'r') as data:
        urls_dl = data.read().splitlines()
        urls = set(urls).difference(urls_dl)

    print("Levels to download: " + str(len(urls)) + "\nDownloading...\n")

# Save downloaded levels into data.txt
with open('data.txt', 'a') as data:
    for url in urls:
        data.write(url + "\n")


def download(url):
    # Set name of level to id if Drive, else set to discord link name.
    if url.startswith('https://drive.google.com/'):
        name = url.split('id=')[-1] + ".rdzip"
    else:
        name = url.split('/')[-1]

    # Append (1) to file name if already exists.
    if os.path.exists(f'{levelpath}/{name}'):
        if samename == "rename":
            name = rename(name, 1)
        elif samename == "skip":
            print(f"Skipping {name}")
            return

    # Download and save zipped level in preZip.
    dwn = requests.get(url, stream=True)
    with open(f'{levelpath}/{name}', 'wb') as f:
        f.write(dwn.content)
    return name


results = ThreadPool(threads).imap_unordered(download, urls)
for chunk in progress.bar(results, expected_size=len(urls)):
    print(f"Done downloading {chunk}" + ' '*30)

print("Done!")
