import std/[asyncdispatch, strformat]
import setup, sheet, download


proc main() {.async.} =
  let downloadFolder = getDownloadFolder()
  echo ""
  let (verifiedOnly, threads) = askUserPrefs()

  echo ""
  echo "Getting levels list."
  let urls = getSiteUrls(verifiedOnly)
  echo fmt"Found {urls.len} levels."
  echo ""

  await downloadLevels(urls, downloadFolder, threads)

  echo "Done downloading! Press Enter to exit..."
  discard stdin.readLine()

when isMainModule:
  waitFor main()
