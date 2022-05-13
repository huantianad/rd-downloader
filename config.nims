--define:ssl
--styleCheck:hint
--gc:orc
--panics:on
when defined(windows):
  switch("passC", "-static")
  switch("passL", "-static")
