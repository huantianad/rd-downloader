import std/[
  asyncdispatch,
  db_sqlite,
  httpclient,
  net,
  os,
  options,
  sequtils,
  tempfiles,
  uri,
  strutils,
]

type
  LevelData = object
    downloadUrl: Uri
    verified: Option[bool]

proc open(connection: string): DbConn =
  open(connection, "", "", "")

proc sqlRowToLevelData(row: Row): LevelData =
  result.downloadUrl = row[0].parseUri()

  let verifiedInt = row[1].parseInt()
  result.verified =
    if verifiedInt > 0: some(true)
    elif verifiedInt < 0: some(false)
    else: none[bool]()

proc getSiteData(client: HttpClient): seq[LevelData] {.gcsafe.} =
  let tempDir = createTempDir("rddownloader_", "")
  defer: removeDir(tempDir)

  const orchardUrl = "https://api.rhythm.cafe/datasette/orchard.db"
  const statusUrl = "https://api.rhythm.cafe/datasette/status.db"
  client.downloadFile(orchardUrl, tempDir / "orchard.db")
  client.downloadFile(statusUrl, tempDir / "status.db")

  let db = open(tempDir / "orchard.db")
  defer: db.close()

  db.exec(sql"ATTACH DATABASE ? as status", tempDir / "status.db")
  db.exec(sql"""
    CREATE TEMP VIEW levels AS
    SELECT level.url, status.approval FROM level
    INNER JOIN status ON status.id = level.id
  """)

  let raw = db.getAllRows(sql"SELECT * from levels")
  result = raw.map(sqlRowToLevelData)

proc getSiteUrls*(verifiedOnly: bool): seq[Uri] {.gcsafe.} =
  var client = newHttpClient()
  var data = client.getSiteData()

  if verifiedOnly:
    data = data.filterIt(it.verified.get(false))

  return data.mapIt(it.downloadUrl)

when isMainModule:
  # let client = newHttpClient()
  # discard client.getSiteData()

  echo getSiteUrls(true).len
  echo getSiteUrls(false).len