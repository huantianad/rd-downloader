-d:ssl
--styleCheck:hint
--gc:orc
--panics:on
when defined(windows):
  -passC: "-static"
  -passL: "-static"
