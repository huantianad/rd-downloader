import std/[sequtils, asyncdispatch, httpclient, net, uri, options]
import jsony

type
  LevelData = object of RootObj
    downloadUrl: Uri
    verified: Option[bool]

proc parseHook*(s: string, i: var int, v: var Uri) {.gcsafe.} =
  var str: string
  parseHook(s, i, str)
  parseUri(str, v)

proc getSheet(client: AsyncHttpClient): Future[seq[LevelData]] {.async, gcsafe.} =
  const url = "https://script.google.com/macros/s/AKfycbzm3I9ENulE7uOmze53cyDuj7Igi7fmGiQ6w045fCRxs_sK3D4/exec"

  let content = await client.getContent(url)
  return content.fromJson(seq[LevelData])

proc getSheetUrls*(verifiedOnly: bool): Future[seq[Uri]] {.async, gcsafe.} =
  var client = newAsyncHttpClient()
  var data = await client.getSheet()

  if verifiedOnly:
    data = data.filterIt(it.verified.get(false))

  return data.mapIt(it.downloadUrl)
