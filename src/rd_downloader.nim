import std/[asyncdispatch, strformat]
import api, download, setup


proc main() {.async.} =
  let downloadFolder = getDownloadFolder()
  echo ""
  let (verifiedOnly, threads) = askUserPrefs()

  echo ""
  echo "Getting levels list."
  let urls = getLevelUrls(verifiedOnly)
  echo fmt"Found {urls.len} levels."
  echo ""

  await downloadLevels(urls, downloadFolder, threads)

  echo "Done downloading! Press Enter to exit..."
  discard stdin.readLine()

when isMainModule:
  waitFor main()
