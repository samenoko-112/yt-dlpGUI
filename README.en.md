# yt-dlpGUI

これは英語版のREADMEです。日本語版はこちら → [ja](README.md)

## Overview
This is a user-friendly GUI wrapper for yt-dlp.  
It was initially created for my personal use and later polished for general use.

## Required Software
- ffmpeg

> Installation on Windows
> ```bash
> winget install Gyan.FFmpeg
> ```

## Main Features
### Search Functionality
You can input search keywords instead of URLs, and the tool will download the top search result.

### Format and Quality Selection
You can choose from `mp4`, `mp3`, or `thumbnail` formats. Note that sometimes `mp4` downloads may result in `mkv` files (planned fix).  
For `mp4`, you can select quality from `Auto`, `144p`, up to `1080p`. For `mp3`, quality ranges from `Auto`, `128kbps` to `320kbps` across 4 levels.

### Playlist Features
- Creating folder with name taken from the playlist title. 
- Add playlist index numbers to filenames.  

### Thumbnail Embedding
Thumbnails can be embedded into the downloaded files.

### Selecting Cookies  
You can use a `cookies.txt` file obtained through browser extensions (e.g., [Chrome](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc), [Firefox](https://addons.mozilla.org/ja/firefox/addon/cookies-txt/)).  
By using `cookies.txt`, you can download member-only videos or videos that require a Premium account.

## Screenshots

![image](https://github.com/user-attachments/assets/03ec1ddd-5d90-4697-a2a5-657e3e3f6af7)

![image](https://github.com/user-attachments/assets/0aa10a48-2673-4991-a48c-dc36aedbb9eb)

## Build it Yourself
You can build the application using `pyinstaller`.

Clone this repository, navigate to the root directory, and run:
```bash
pyinstaller yt-dlpGUI.spec
```

## Verified Operating Systems
- Microsoft Windows 10.0.19045.5371 (amd64)
- macOS 15.2 (arm64)
- Ubuntu 24.04 (amd64)

Packages for operating systems other than Windows are not distributed.  
To run the application, you need to clone this repository, install the dependencies listed in `requirements.txt`,  
and additionally install `ffmpeg` and, in some cases, `libmpv`.