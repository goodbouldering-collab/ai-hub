param(
  [string]$VoiceName = "ja-JP-NanamiNeural",
  [string]$Rate = "+8%"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$Root = Split-Path -Parent $PSScriptRoot
$Slug = "ai-consult-hikone-20260629"
$NarrationPath = Join-Path $Root "content\media\$Slug\narration.txt"
$OutDir = Join-Path $Root "site\static\media\$Slug"
$TmpDir = Join-Path $Root "_tmp\$Slug"
$Mp3Path = Join-Path $OutDir "ai-consult-hikone-narration.mp3"
$WavPath = Join-Path $TmpDir "ai-consult-hikone-narration.wav"
$VttPath = Join-Path $OutDir "ai-consult-hikone-captions.vtt"
$SrtPath = Join-Path $TmpDir "edge-subtitles.srt"
$NarrationCopyPath = Join-Path $OutDir "ai-consult-hikone-narration.txt"

if (!(Test-Path $NarrationPath)) {
  throw "Narration source not found: $NarrationPath"
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
New-Item -ItemType Directory -Force -Path $TmpDir | Out-Null

$env:AI_CONSULT_ROOT = $Root
$env:AI_CONSULT_SLUG = $Slug
$env:AI_CONSULT_VOICE = $VoiceName
$env:AI_CONSULT_RATE = $Rate

@'
from pathlib import Path
import asyncio
import os
import edge_tts

root = Path(os.environ["AI_CONSULT_ROOT"])
slug = os.environ["AI_CONSULT_SLUG"]
voice = os.environ["AI_CONSULT_VOICE"]
rate = os.environ["AI_CONSULT_RATE"]

text_path = root / "content" / "media" / slug / "narration.txt"
out_dir = root / "site" / "static" / "media" / slug
tmp_dir = root / "_tmp" / slug
media_path = out_dir / "ai-consult-hikone-narration.mp3"
srt_path = tmp_dir / "edge-subtitles.srt"
vtt_path = out_dir / "ai-consult-hikone-captions.vtt"
copy_path = out_dir / "ai-consult-hikone-narration.txt"

text = text_path.read_text(encoding="utf-8")

async def main():
    communicate = edge_tts.Communicate(
        text,
        voice=voice,
        rate=rate,
        boundary="SentenceBoundary",
    )
    submaker = edge_tts.SubMaker()
    with media_path.open("wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)
    srt = submaker.get_srt()
    srt_path.write_text(srt, encoding="utf-8")
    lines = ["WEBVTT", ""]
    for line in srt.splitlines():
        if "-->" in line:
            line = line.replace(",", ".")
        lines.append(line)
    vtt_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    copy_path.write_text(text, encoding="utf-8")

asyncio.run(main())
print(media_path)
print(vtt_path)
'@ | python -

ffmpeg -y -i $Mp3Path -ar 48000 -ac 2 $WavPath

Write-Output "Wrote $Mp3Path"
Write-Output "Wrote $WavPath"
Write-Output "Wrote $VttPath"
Write-Output "Wrote $NarrationCopyPath"
