import json
import os
import zipfile

import requests


# Start and stop for downloading; index starts at 0, start inclusive, end non-inclusive
start = 0
end = 1

# Find levels folder
levelpath = os.path.join('C:\\', 'Users', os.getlogin(), 'Documents', 'Rhythm Doctor', 'Levels')


# Download list of files from thing
thing = requests.get(
    'https://script.google.com/macros/s/AKfycbzm3I9ENulE7uOmze53cyDuj7Igi7fmGiQ6w045fCRxs_sK3D4/exec').content
stuff = json.loads(thing.decode('utf-8'))

# Loop through selected levels
for level in stuff[start:end]:
    # Get url and file name of level
    url = level['download_url']
    name = url.split('/')[-1]
    print(name)

    # Download and save zipped level in preZip
    download = requests.get(url)
    with open(f'{name}', 'wb') as f:
        f.write(download.content)

    # Unzip file into level directory
    with zipfile.ZipFile(f'{name}', 'r') as zip_ref:
        zip_ref.extractall(f'{levelpath}/{name}')

    # Delete unzipped file
    os.remove(f'{name}')
