include prelude
import std/[httpclient, net, uri, asyncdispatch, asyncfile, rdstdin, sugar]

import suru

import sheet

proc getFilename(url: Uri, resp: AsyncResponse): string =
  ## Extracts the filename when downloading a file
  let (_, name, ext) = url.path.splitFile
  if ext == ".rdzip" or ext == ".zip":
    return name & ext

  let cd = resp.headers["Content-Disposition"]
  for pair in cd.split(';'):
    result = pair.strip()
    if result.startsWith("filename=\""):
      result.removePrefix("filename=\"")
      result.removeSuffix("\"")
      return

  echo fmt"Failed to find filename for {url}, returning 'UNKNOWN.rdzip'"
  return "UNKNOWN.rdzip"


proc ensureFilename(path: string): string =
  ## Creates a unique filename for a given path by adding (#)
  ## to the filename.
  if not path.fileExists:
    return path

  let (directory, name, ext) = path.splitFile

  var index = 2
  while joinPath(directory, fmt"{name} ({index}){ext}").fileExists:
    index += 1

  joinPath(directory, fmt"{name} ({index}){ext}")


proc downloadLevel(client: AsyncHttpClient, url: Uri, folder: string) {.async.} =
  ## Downloads a file into the given folder, automatically gets filename
  ## from the url, and ensures it is unique
  let resp = await client.get(url)

  let filename = getFilename(url, resp)
  let fullPath = joinPath(folder, filename).ensureFilename()

  let asyncFile = fullPath.openAsync(fmWrite)
  try:
    await asyncFile.writeFromStream(resp.bodyStream)
  finally:
    asyncFile.close()

proc downloadLevelSafe(client: AsyncHttpClient, url: Uri, folder: string) {.async.} =
  ## Downloads a file into the given folder, automatically gets filename
  ## from the url, and ensures it is unique. Should never throw error.
  try:
    await downloadLevel(client, url, folder)
  except:
    echo getCurrentExceptionMsg()

proc downloadLevels(urls: seq[Uri], folder: string, threads: Positive = 8): Future[void] =
  ## Concurrently downloads multiple urls into given folder.
  ## `threads` is the maximum concurrency of the download.
  var mainFuture = newFuture[void]("downloadLevels")

  var clients = newSeqWith(threads, newAsyncHttpClient())
  var currentUrlIndex, finishedClients: int

  var bar = initSuruBar(threads + 1)
  bar[threads].total = urls.len
  bar.setup()

  mainFuture.addCallback do ():
    bar.finish()

  for i in 0..<threads:
    capture i:
      proc onProgressChanged(total, progress, speed: BiggestInt) {.async.} =
        bar[i].total = total.int
        bar[i].progress = progress.int
        bar.update()

      clients[i].onProgressChanged = onProgressChanged

  proc bump(clientIndex: int) =
    if currentUrlIndex == urls.len:
      inc finishedClients
      if finishedClients == threads:
        mainFuture.complete()
      return

    let currentClient = clients[clientIndex]
    let currentUrl = urls[currentUrlIndex]
    inc currentUrlIndex

    var fut = currentClient.downloadLevelSafe(currentUrl, folder)
    fut.addCallback do ():
      # Do I want to do this bit before the update?
      bar[clientIndex].progress = bar[clientIndex].total
      bar.update()

      bar[clientIndex].reset()
      inc bar[threads]
      bar.update()

      bump(clientIndex)

  for i in 0..<threads:
    bump(i)

  return mainFuture

const testUrls = [
  "https://cdn.discordapp.com/attachments/611380148431749151/962499843018862592/placeboing_-_BANAS.rdzip",
  "https://drive.google.com/uc?export=download&id=1LZ5KWG4KCL1Or-kSYimbVaSFIoTrGgsI",
  "http://www.bubbletabby.com/MATTHEWGU4_-_Hail_Satan_Metal_Cover.rdzip"
].map(parseUri)

proc getDownloadFolder(): string =
  result = "./rd_downloader/"

  let verb =
    if result.existsOrCreateDir:
      "existing"
    else:
      "just created"

  echo fmt"Downloading in {verb} folder at {result.expandFilename}"

proc askUserPrefs(): tuple[verifiedOnly: bool, threads: int] =
  while true:
    let input = readLineFromStdin("Would you like to download only checked levels? (Y/n) ").toLowerAscii
    if input == "y" or input == "yes" or input == "":
      result[0] = true
      break
    elif input == "n" or input == "no":
      result[0] = false
      break
    else:
      echo "Invalid input!"

  while true:
    let input = readLineFromStdin("How many download threads would you like to use? (Default: 8) ")
    if input == "":
      result[1] = 8
      break
    else:
      try:
        result[1] = input.parseInt()
        if result[1] < 0: raise newException(ValueError, "")
        break
      except ValueError:
        echo "Input must be an integer greater than 0!"


proc main() {.async.} =
  let downloadFolder = getDownloadFolder()
  let (verifiedOnly, threads) = askUserPrefs()

  echo "Getting levels list."
  var client = newAsyncHttpClient()
  let urls = await client.getSheetUrls(verifiedOnly)
  echo fmt"Found {urls.len} levels."

  await downloadLevels(urls, downloadFolder, threads)

when isMainModule:
  waitFor main()
