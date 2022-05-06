import std/[strformat, os, rdstdin, strutils]

proc getDownloadFolder*(): string =
  result = "./downloads/"

  let verb =
    if result.existsOrCreateDir: "existing"
    else: "just created"

  echo fmt"Downloading in {verb} folder at {result.expandFilename}"

proc askUserPrefs*(): tuple[verifiedOnly: bool, threads: int] =
  while true:
    let input = readLineFromStdin("Would you like to download only checked levels? (Y/n) ").toLowerAscii
    if input == "y" or input == "yes" or input == "":
      result.verifiedOnly = true
      break
    elif input == "n" or input == "no":
      result.verifiedOnly = false
      break
    else:
      echo "Invalid input!"

  while true:
    let input = readLineFromStdin("How many download threads would you like to use? (Default: 3) ")
    if input == "":
      result.threads = 3
      break
    else:
      try:
        result.threads = input.parseInt()
        if result.threads < 0: raise newException(ValueError, "")
        break
      except ValueError:
        echo "Input must be an integer greater than 0!"
