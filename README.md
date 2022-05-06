# rd-downloader
Simple Bulk Downloader for the [RD custom levels site](https://auburnsummer.github.io/rdlevels/).

This project was over at [SimpleDownload](https://github.com/huantianad/SimpleDownload) for a bit, check there for older releases.

## Features
- Simple interactive text-based interface
- Choose between downloading all or only checked levels
- Concurrent downloads for a much quicker experience
   - Configurable thread count

## Usage
1. Download and run the latest release [here](https://github.com/huantianad/rd-downloader/releases/).
2. Follow the prompts. If you don't know how many download threads to use, just use the default.
3. The program will create a new sub-folder called `downloads` and download all the levels there. (It might seem like the program is stuck on the last level, it's probably just a big file.)
4. Profit.

Note: if you have the full game, you can select multiple levels when importing to import many at the same time.
If you do not have the full game, you can use [7-zip](https://www.7-zip.org/) to unzip multiple rdzips at the same time.

## Run From Source
If you don't want to use the exe file to run the program, you can also run the program via python directly.
1. Get yourself [nim](https://github.com/dom96/choosenim).
2. Clone the repository: `git clone https://github.com/huantianad/rd-downloader.git`
3. Install and dependencies and build the project: `nimble build -d:release`
4. Run program created at `rd_downloader.exe`.
5. Follow the prompts.
6. Profit.
