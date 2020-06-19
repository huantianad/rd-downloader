import json
import os
import zipfile

import requests

# Find levels folder
levelpath = os.path.join('C:\\', 'Users', os.getlogin(), 'Documents', 'Rhythm Doctor', 'Levels')

# Download list of files from thing
thing = requests.get(
    'https://script.google.com/macros/s/AKfycbzm3I9ENulE7uOmze53cyDuj7Igi7fmGiQ6w045fCRxs_sK3D4/exec').content
stuff = json.loads(thing.decode('utf-8'))

print("Total number of levels: " + str(len(stuff)) + "\n")

# Start and stop for downloading; index starts at 0, start inclusive, end non-inclusive
start = int(input("Level to start at (index starts at 0): "))
end = int(input("Level to end at (non-inclusive): "))

if end - start == 1:
    print("Looping through 1 level.")
else:
    print("Looping through " + str(end - start) + " levels.")
print("\n")

# Loop through selected levels
for level in stuff[start:end]:
    # Get url and file name of level
    url = level['download_url']
    name = url.split('/')[-1]
    print(f"Downloading {name}")

    # Download and save zipped level in preZip
    download = requests.get(url)
    with open(f'{name}', 'wb') as f:
        f.write(download.content)

    # Unzip file into level directory
    with zipfile.ZipFile(f'{name}', 'r') as zip_ref:
        zip_ref.extractall(f'{levelpath}/{name}')

    # Delete unzipped file
    os.remove(f'{name}')
