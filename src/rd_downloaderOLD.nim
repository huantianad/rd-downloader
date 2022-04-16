include prelude
import std/[httpclient, net, uri, options, asyncfutures, asyncdispatch]

import sheet

proc getFilename(url: Uri): string =
  let (_, name, ext) = url.path.splitFile
  if ext == ".rdzip" or ext == ".zip":
    return name & ext

  raise newException(ValueError, fmt"{url} not implemented")

  # let resp = client.get(url)
  # echo resp.headers
  # let cd = resp.headers["Content-Disposition"]

  # echo resp

proc ensureFilename(path: string): string =
  if not path.fileExists:
    return path

  let (directory, name, ext) = path.splitFile

  var index = 2
  while joinPath(directory, fmt"{name} ({index}){ext}").fileExists:
    index += 1

  joinPath(directory, fmt"{name} ({index}){ext}")


proc softError(exc: ref Exception) =
  ## Tell the user about this exception without crashing the program
  echo exc.msg

proc downloadLevels(levelUrls: seq[Uri], threads: int = 8): Future[void] {.gcsafe.} =
  var mainFuture = newFuture[void]("rd_downloader.downloadLevels")

  var clients = newSeqWith(threads, newAsyncHttpClient())
  var remainingUrls = levelUrls
  var startedThreads = 0
  var completedThreads = 0

  proc downloadLevel(client: AsyncHttpClient, url: Uri, id: int) {.gcsafe.} =
    let filename = ("./downloads" / getFilename(url)).ensureFilename
    echo filename
    echo id

    var fut = client.downloadFile(url, filename)

    fut.addCallback do ():
      if fut.failed:
        raise fut.error
        # mainFuture.fail(fut.error)

      while true:
        if remainingUrls.len == 0:
          completedThreads += 1
          if completedThreads == startedThreads:
            mainFuture.complete()
          return

        try:
          client.downloadLevel(remainingUrls.pop(), id)
          break
        except Exception as exc:
          softError exc


  for i in 0..<threads:
    while true:
      if remainingUrls.len == 0:
        if i == 0:
          # We went through all of the urls and they all raised an exception
          mainFuture.complete()
        break

      try:
        clients[i].downloadLevel(remainingUrls.pop(), i)
        startedThreads += 1
        break
      except Exception as exc:
        softError exc


  return mainFuture

const testUrls = [
  "https://cdn.discordapp.com/attachments/611380148431749151/922477947716251658/Plum_-_MEGAMIX_1-0-0.rdzip",
  "https://drive.google.com/uc?export=download&id=1LZ5KWG4KCL1Or-kSYimbVaSFIoTrGgsI",
  "http://www.bubbletabby.com/MATTHEWGU4_-_Hail_Satan_Metal_Cover.rdzip"
].map(parseUri)

proc main() {.async.} =
  if not dirExists("./downloads"):
    createDir("./downloads")

  var client = newAsyncHttpClient()
  let urls = await client.getSheetUrls(true)

  # await downloadLevels(urls[0..10])

  # for url in urls:
  #   if "drive.google" in $url:
  #     echo url

when isMainModule:
  waitFor main()
