import configparser
import json
import os
from multiprocessing.pool import ThreadPool

import requests

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


# Create function to handle renaming.
def rename(name, index):
    if os.path.exists(f'{levelpath}/{name} ({index})'):
        return rename(name, index + 1)
    else:
        return f"{name} ({index})"


# Download list of files from thing.
thing = requests.get(
    'https://script.google.com/macros/s/AKfycbzm3I9ENulE7uOmze53cyDuj7Igi7fmGiQ6w045fCRxs_sK3D4/exec').content
stuff = json.loads(thing.decode('utf-8'))

# Prompt user for start and stop of levels to download
print("Total number of levels: " + str(len(stuff)) + "\n")
start = int(input("Level to start at (index starts at 0): "))
end = int(input("Level to end at (non-inclusive): "))

if end - start == 1:
    print("Looping through 1 level.")
else:
    print("Looping through " + str(end - start) + " levels.")
print("\n")


urls = []

for level in stuff[start:end]:
    urls.append(level['download_url'])


def download(url):
    # Set name of level to id if Drive, else set to discord link name.
    if url.startswith('https://drive.google.com/'):
        name = url.split('id=')[-1]
    else:
        name = url.split('/')[-1]

    # Append (1) to file name if already exists.
    if os.path.exists(f'{levelpath}/{name}'):
        if samename == "rename":
            name = rename(name, 1)
        elif samename == "skip":
            print(f"Skipping {name}")
            return

    print(f"Downloading {name}")
    print("\n")

    # Download and save zipped level in preZip.
    dwn = requests.get(url, stream=True)
    with open(f'{levelpath}/{name}', 'wb') as f:
        f.write(dwn.content)
    return url


# The amount of simultaneous downloads. Increasing will increase speed, but will be capped by your network speed.
threads = 8
results = ThreadPool(8).imap_unordered(download, urls)
for r in results:
    print(r)
