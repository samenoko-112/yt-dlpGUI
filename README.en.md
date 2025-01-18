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
- Create folders named after playlist titles and save downloaded files inside.  
- Add playlist index numbers to filenames.  
These features are useful for downloading playlists.

### Thumbnail Embedding
Thumbnails can be embedded into the downloaded files.

### Cookie Selection
You can select a `cookies.txt` or other text file containing login information to download videos that require authentication.

## Screenshots

![image](https://github.com/user-attachments/assets/03ec1ddd-5d90-4697-a2a5-657e3e3f6af7)

![image](https://github.com/user-attachments/assets/0aa10a48-2673-4991-a48c-dc36aedbb9eb)

## Build it Yourself
You can build the application using `pyinstaller`.

Clone this repository, navigate to the root directory, and run:
```bash
pyinstaller yt-dlpGUI.spec
```

## Compatibility with Other OSes
It has been tested and confirmed to work on macOS.  
Run the following command to start the application:
```bash
python main.py
```
