import std/[
  asyncdispatch,
  asyncfile,
  asyncfutures,
  cookies,
  httpclient,
  net,
  options,
  os,
  sequtils,
  strformat,
  strutils,
  strtabs,
  uri,
]
import suru

proc getFilename(url: Uri, resp: AsyncResponse): Option[string] =
  ## Extracts filename from a url/response headers.
  ## Either uses last element in url, or Content-Disposition header.
  # Check if filename is already in URL
  let (_, name, ext) = url.path.splitFile
  if ext == ".rdzip" or ext == ".zip":
    return some(name & ext)

  # Otherwise extract from Content-Disposition header
  const prefix = "attachment;"
  let cd = resp.headers["Content-Disposition"]

  if cd.startsWith(prefix):
    let cdData = cd[prefix.len..^1].parseCookies()
    if "filename" in cdData:
      return some(cdData["filename"])

proc ensureFilename(path: string): string =
  ## Creates a unique filename for a given path by adding (#) to the filename.
  if not path.fileExists:
    return path

  let (directory, name, ext) = path.splitFile

  var index = 2
  while fileExists(directory / fmt"{name} ({index}){ext}"):
    index += 1

  directory / fmt"{name} ({index}){ext}"

proc downloadLevel(client: AsyncHttpClient, url: Uri, folder: string) {.async.} =
  ## Downloads a file into the given folder, automatically gets filename
  ## from the url, and ensures it is unique
  let resp = await client.get(url)

  let filename = block:
    let rawFilename = getFilename(url, resp)
    if rawFilename.isSome:
      rawFilename.get()
    else:
      echo fmt"Failed to get filename for url: {url}"
      "UNKNOWN.rdzip"

  let fullPath = ensureFilename(folder / filename)

  let asyncFile = fullPath.openAsync(fmWrite)
  defer: asyncFile.close()
  await asyncFile.writeFromStream(resp.bodyStream)


proc downloadLevelSafe(client: AsyncHttpClient, url: Uri, folder: string) {.async.} =
  ## Downloads a file into the given folder, automatically gets filename
  ## from the url, and ensures it is unique. Should never throw error.
  try:
    await downloadLevel(client, url, folder)
  except:
    echo fmt"Failed to download '{url}'. Error message:"
    echo getCurrentExceptionMsg()

proc downloadLevels*(urls: seq[Uri], folder: string, threads: Positive = 8): Future[void] =
  ## Concurrently downloads multiple urls into given folder.
  ## `threads` is the maximum concurrency of the download.
  var mainFuture = newFuture[void]("downloadLevels")

  var clients = newSeqWith(threads, newAsyncHttpClient())
  var currentUrlIndex, finishedClients: int

  var bar = initSuruBar()
  bar[0].total = urls.len
  bar.setup()

  mainFuture.addCallback do ():
    bar.finish()
    for client in clients:
      client.close()

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
      inc bar
      bar.update()

      bump(clientIndex)

  for i in 0..<threads:
    bump(i)

  return mainFuture
