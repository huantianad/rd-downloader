version     = "2.1.2"
author      = "huantian"
description = "Simple Bulk Downloader for the Rhythm Doctor custom levels site."
license     = "MIT"
srcDir      = "src"
bin         = @["rd_downloader"]

requires "nim >= 1.6.0"
requires "jsony >= 1.1.1"
requires "suru >= 0.3.1"


task buildDev, "Build for usage during development":
    exec "nimble build -d:ssl"

task buildProd, "Build for production":
    exec "nimble build -d:ssl -d:release"

task buildCI, "Build for production on the CI machine":
    exec "nimble build -d:ssl -d:release -y"