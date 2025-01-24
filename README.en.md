# yt-dlpGUI

> [!CAUTION]
> I have decided to temporarily suspend development due to a loss of motivation.  
> I may resume it again if I feel inclined to do so in the future.

これは英語版のREADMEです。日本語版はこちら→ [ja](README.ja.md)

## Overview
A user-friendly GUI wrapper for yt-dlp.  
Originally created for personal use, now refined and improved for general use.

## Required Software
- ffmpeg

> Windows Installation:
> ```bash:terminal
> winget install Gyan.FFmpeg
> ```

## Key Features
### Search Function
Download the top search result using keywords instead of direct URLs.

### Format & Quality Selection
Available formats:  
`mp4, mp3, m4a, wav, opus, flac, thumbnail`  
Quality options:  
- mp4: Automatic, 144p to 2160p  
- mp3/m4a: Automatic, 128kbps to 320kbps (4 levels)

### Playlist Handling
- Creates folders using playlist titles  
- Adds playlist indexes to filenames

### Thumbnail Embedding
Embeds thumbnails into files.  
*Not supported for WAV and Opus formats*

### Cookie Selection
Use cookies.txt obtained through browser extensions ([Chrome](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc), [Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)) to download:  
- Members-only content  
- Premium content  
- Age-restricted videos

### HDR Prioritization
Prioritizes HDR videos when available.

### Aria2 Integration
Utilizes external downloader `aria2` for potentially faster downloads.

## Screenshots

![image](https://github.com/user-attachments/assets/41a929f1-b9e3-497f-afb4-3335e6de8198)

![image](https://github.com/user-attachments/assets/239eef17-f7b3-4133-89bb-ff72e0d44a2e)

## Build from Source
Build using pyinstaller:

1. Clone this repository
2. Navigate to the directory
3. Run:
```bash
pyinstaller yt-dlpGUI.spec
```

Built files will be in `/dist`

## Verified OS Environments
- Microsoft Windows 10.0.19045.5371 (amd64)
- macOS 15.2 (arm64)
- Ubuntu 24.04 (amd64)

No pre-built packages available for non-Windows systems.  
For other OSes, clone the repository and install:
- Requirements from requirements.txt
- ffmpeg
- libmpv (if required)

## Contributors
[@samenoko-112 (Developer)](https://github.com/samenoko-112)  
[@reindex-ot (Translation)](https://github.com/reindex-ot)
