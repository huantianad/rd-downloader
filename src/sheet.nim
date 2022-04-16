include prelude
import std/[asyncdispatch, httpclient, net, uri, options]

import jsony

type
  LevelData = object of RootObj
    downloadUrl: Uri
    previewImg: Option[Uri]
    lastUpdated: DateTime
    maxBpm: Option[float]
    minBpm: Option[float]
    singlePlayer: bool
    twoPlayer: bool
    verified: Option[bool]

proc parseHook*(s: string, i: var int, v: var Uri) {.gcsafe.} =
  var str: string
  parseHook(s, i, str)
  parseUri(str, v)

proc parseHook*(s: string, i: var int, v: var Option[Uri]) {.gcsafe.} =
  # Option[Uri] can either be `false` or `"https://stuff.com"`
  # if it even parses as a bool, assume false and return none()
  try:
    var maybeBool: bool
    parseHook(s, i, maybeBool)
    v = none[Uri]()
  except JsonError:
    var uri: Uri
    parseHook(s, i, uri)
    v = some(uri)

proc parseHook*(s: string, i: var int, v: var DateTime) {.gcsafe.} =
  var str: string
  parseHook(s, i, str)
  v = str.parse("yyyy-MM-dd'T'HH:mm:ss'.'fffz")

proc getSheet(client: AsyncHttpClient): Future[seq[LevelData]] {.async, gcsafe.} =
  const url = "https://script.google.com/macros/s/AKfycbzm3I9ENulE7uOmze53cyDuj7Igi7fmGiQ6w045fCRxs_sK3D4/exec"

  let content = await client.getContent(url)
  return content.fromJson(seq[LevelData])

proc getSheetUrls*(client: AsyncHttpClient, verifiedOnly: bool): Future[seq[Uri]] {.async, gcsafe.} =
  var data = await client.getSheet()

  if verifiedOnly:
    data = data.filterIt(it.verified.get(false))

  return data.mapIt(it.downloadUrl)
