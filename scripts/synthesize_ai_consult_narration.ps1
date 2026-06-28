param(
  [string]$VoiceName = "Microsoft Haruka Desktop",
  [int]$Rate = -1
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$Root = Split-Path -Parent $PSScriptRoot
$Slug = "ai-consult-hikone-20260629"
$NarrationPath = Join-Path $Root "content\media\$Slug\narration.txt"
$OutDir = Join-Path $Root "site\static\media\$Slug"
$OutFile = Join-Path $OutDir "ai-consult-hikone-narration.wav"

if (!(Test-Path $NarrationPath)) {
  throw "Narration source not found: $NarrationPath"
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$Text = Get-Content -Raw -Encoding UTF8 $NarrationPath
$Voice = New-Object -ComObject SAPI.SpVoice
$Voice.Rate = $Rate
$Voice.Volume = 100

$Installed = $Voice.GetVoices()
for ($i = 0; $i -lt $Installed.Count; $i++) {
  $Candidate = $Installed.Item($i)
  if ($Candidate.GetDescription() -like "*$VoiceName*") {
    $Voice.Voice = $Candidate
    break
  }
}

$Stream = New-Object -ComObject SAPI.SpFileStream
try {
  $Stream.Open($OutFile, 3, $false)
  $Voice.AudioOutputStream = $Stream
  [void]$Voice.Speak($Text, 0)
} catch {
  throw "Local Windows TTS failed. This environment may not have an enabled Japanese SAPI voice. Original error: $($_.Exception.Message)"
} finally {
  if ($Stream) {
    try { $Stream.Close() } catch {}
  }
}

Write-Output "Wrote $OutFile"
