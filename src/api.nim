import std/[
  db_sqlite,
  httpclient,
  net,
  options,
  os,
  sequtils,
  tempfiles,
  uri,
]

proc open(connection: string): DbConn =
  open(connection, "", "", "")

proc getLevelUrls(client: HttpClient, verifiedOnly: bool): seq[Uri] {.gcsafe.} =
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
      SELECT
        level.url,
        COALESCE(status.approval, 0) AS approval
      FROM
        level
      LEFT JOIN status ON status.id = level.id
  """)

  let query =
    if verifiedOnly:
      sql"SELECT url from levels WHERE approval > 0"
    else:
      sql"SELECT url from levels"

  db.getAllRows(query).mapIt(it[0].parseUri)

proc getLevelUrls*(verifiedOnly: bool): seq[Uri] {.gcsafe.} =
  var client = newHttpClient()
  defer: client.close()

  client.getLevelUrls(verifiedOnly)
