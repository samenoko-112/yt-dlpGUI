from flet import *
from yt_dlp import YoutubeDL
import re
import os
import json
import sys
import locale
import requests
import webbrowser

def resource_path(relative_path):
    """Obtaining PyInstaller-enabled resource paths"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_version():
    try:
        with open(resource_path("assets/version.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("version")
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
    
def get_tag():
    url = f"https://api.github.com/repos/samenoko-112/yt-dlpGUI/releases/latest"
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("tag_name")
    else:
        return None

def check_update(local_version,latest_version):
    if local_version and latest_version:
        if local_version != latest_version:
            return f"https://github.com/samenoko-112/yt-dlpGUI/releases/tag/{latest_version}"
        else:
            return None
    else:
        return None

def detect_system_locale():
    """Determine language based on system locale"""
    lang, _ = locale.getdefaultlocale()
    return "ja" if lang and lang.startswith("ja") else "en"

def load_locale(locale: str):
    """Load translations in a given language"""
    global translations, current_locale

    try:
        locale_path = resource_path(f"locale/{locale}.json")
        with open(locale_path, "r", encoding="utf-8") as f:
            translations = json.load(f)
    except FileNotFoundError:
        print(f"Error: locale/{locale}.json not found")
        translations = {}

def t(key: str) -> str:
    """Get Translation Key"""
    return translations.get(key, key)

# Keep current language
current_locale = detect_system_locale()
translations = {}

# Detect system locale and load language
load_locale(detect_system_locale())

outpath = os.path.normpath(os.path.expanduser('~') + "/ytdlp")
cookie = None

mp4_qualitys = [dropdown.Option(key="Auto"), dropdown.Option(key="144p"), dropdown.Option(key="240p"), dropdown.Option(key="360p"), dropdown.Option(key="480p"), dropdown.Option(key="720p"), dropdown.Option(key="1080p"), dropdown.Option(key="1440p"),dropdown.Option(key="2160p")]
mp3_qualitys = [dropdown.Option(key="Auto"), dropdown.Option(key="128kbps"), dropdown.Option(key="192kbps"), dropdown.Option(key="256kbps"), dropdown.Option(key="320kbps")]

def main(page: Page):
    page.title = f"yt-dlpGUI - {get_version()}"
    page.window.width = 500
    page.window.height = 900
    page.padding = 16
    page.window.min_height = 900
    page.window.min_width = 500
    page.window.icon = resource_path("assets/icon2.ico")

    def w_init():
        latest = check_update(get_version(),get_tag())
        if latest:
            snack_bar = SnackBar(content=Row([Text(t("update_available")),TextButton(t("download_update"),on_click=lambda _: webbrowser.open(latest))]))
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()
        else:
            snack_bar = SnackBar(Text(t("no_update")))
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()

    w_init()

    def open_about_dialog(e):
        page.overlay.append(about_dialog)
        about_dialog.open = True
        page.update()

    def close_about_dialog(e):
        about_dialog.open = False
        page.update()

    about_dialog = AlertDialog(
        title=Text(t("about_title")),
        content=Column([
            Text(t("about_text").format(version=get_version())),
        ]),
        actions=[
            TextButton(t("close"),on_click=close_about_dialog)
        ],
        actions_alignment=MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
        modal=True
    )

    page.appbar = AppBar(
        title=Text("yt-dlpGUI"),
        center_title=False,
        bgcolor=Colors.SURFACE,
        actions=[
            IconButton(icon=Icons.INFO,on_click=open_about_dialog),
            IconButton(icon=Icons.REFRESH,on_click=lambda _: w_init())
        ]
    )

    def change_ext(e):
        if ext_sel.value == "mp4":
            quality_sel.options = mp4_qualitys
            quality_sel.value = mp4_qualitys[0].key
        elif ext_sel.value == "mp3":
            quality_sel.options = mp3_qualitys
            quality_sel.value = mp3_qualitys[0].key
        elif ext_sel.value == "m4a":
            quality_sel.options = mp3_qualitys
            quality_sel.value = mp3_qualitys[0].key
        else:
            quality_sel.options = []
            quality_sel.value = "None"
        quality_sel.update()

    def sel_path(e: FilePickerResultEvent):
        global outpath
        before = outpath
        outpath = e.path if e.path else before
        outpath_input.value = os.path.normpath(outpath)
        outpath_input.update()
    
    def sel_cookie(e: FilePickerResultEvent):
        global cookie
        if e.files:
            cookie = e.files[0].path
        else:
            cookie = ""
        cookie_input.value = cookie
        cookie_input.update()

    # Function to delete ANSI code
    def remove_ansi_codes(text):
        return re.sub(r'\x1b\[[0-9;]*m', '', text)

    # ダウンロード関数
    def download(e):
        # Set download button to “Downloading
        dl_btn.disabled = True
        dl_btn.text = t("download_in_progress")
        dl_btn.icon = Icons.DOWNLOADING
        dl_btn.update()

        # Initialize progress bar and status
        progress_bar.value = None
        progress_bar.update()
        status_text.value = t("status_starting")
        status_text.update()

        # yt-dlp hook functions
        def hook(d):
            progress_bar.value = None
            progress_bar.update()
            status_text.value = t("status_processing")
            status_text.update()

            if use_aria2c.value == False:

                if d["status"] == "downloading":
                    # Convert progress from percent to bar
                    progress = remove_ansi_codes(d.get("_percent_str", "0%"))
                    progress = progress.strip('%')
                    try:
                        progress_float = float(progress)
                        progress_bar.value = progress_float / 100
                        progress_bar.update()
                    except ValueError:
                        pass

                    # View other progress information
                    speed = remove_ansi_codes(d.get("_speed_str", t("unknown")))
                    eta = remove_ansi_codes(d.get("_eta_str", t("unknown")))

                    status_text.value = t("status_progress").format(progress=progress, speed=speed, eta=eta)
                    status_text.update()

                    file = os.path.normpath(remove_ansi_codes(d.get("filename")))
                    now_title.value = file.replace(outpath+"\\", "")
                    now_title.update()

                elif d["status"] == "postprocessing":
                    progress_bar.value = None
                    progress_bar.update()
                    status_text.value = t("status_postprocessing")
                    status_text.update()

            else:
                progress_bar.value = None
                progress_bar.update()
                status_text.value = t("download_in_progress")
                status_text.update()

                file = os.path.normpath(remove_ansi_codes(d.get("filename")))
                now_title.value = file.replace(outpath+"\\", "")
                now_title.update()

                if d["status"] == "postprocessing":
                    progress_bar.value = None
                    progress_bar.update()
                    status_text.value = t("status_postprocessing")
                    status_text.update()

        url = url_input.value
        quality = quality_sel.value
        ext = ext_sel.value

        ydl_opts = {
            "outtmpl": f"{outpath}/%(title)s.%(ext)s",
            "format_sort": ['codec:avc:aac', 'res:1080', 'hdr:sdr'],
            "format": "bv+ba",
            "progress_hooks": [hook],
            "postprocessors": [
                {
                    "key": "FFmpegMetadata",
                    "add_metadata": True
                }
            ],
            "quiet": False,
            "ignoreerrors": True,
            "default_search": "ytsearch",
        }

        # cookie file
        if cookie_input.value:
            ydl_opts["cookiefile"] = cookie

        if use_aria2c.value:
            ydl_opts["external_downloader"] = "aria2c"
            ydl_opts["external_downloader_args"] = ['-x', '16', '-s', '16', '-k', '1M']

        # thumbnail
        if ext == "thumbnail":
            ydl_opts["writethumbnail"] = True
            ydl_opts["skip_download"] = True
            ydl_opts["outtmpl"] = f"{outpath}/%(title)s.%(ext)s"

        # Create folders with playlist titles
        if playlist.value:
            ydl_opts["outtmpl"] = f"{outpath}/%(playlist_title)s/%(title)s.%(ext)s"

        # Add playlist index to file name
        if playlist_index.value:
            ydl_opts["outtmpl"] = f"{outpath}/%(playlist_index)02d - %(title)s.%(ext)s" if not playlist.value else f"{outpath}/%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s"

        # Formatting
        if ext == "mp4":
            ydl_opts['merge_output_format'] = 'mp4'
            quality_formats = {
                "Auto": ['codec:avc:aac', 'res:1080', 'hdr:sdr'],
                "144p": ['codec:avc:aac', 'res:144', 'hdr:sdr'],
                "240p": ['codec:avc:aac', 'res:240', 'hdr:sdr'],
                "360p": ['codec:avc:aac', 'res:360', 'hdr:sdr'],
                "480p": ['codec:avc:aac', 'res:480', 'hdr:sdr'],
                "720p": ['codec:avc:aac', 'res:720', 'hdr:sdr'],
                "1080p": ['codec:avc:aac', 'res:1080', 'hdr:sdr'],
                "1440p": ['codec:avc:aac', 'res:1440', 'hdr:sdr'],  # 2K
                "2160p": ['codec:avc:aac', 'res:2160', 'hdr:sdr'],  # 4K
            }
            ydl_opts["format_sort"] = quality_formats.get(quality, quality_formats["Auto"])

            if enable_hdr.value:
                ydl_opts["format_sort"] = [item for item in ydl_opts["format_sort"] if item != 'hdr:sdr']
                ydl_opts["format_sort"] = ['vcodec:vp9', 'vcodec:av01'] + ydl_opts["format_sort"]
                ydl_opts["format_sort"] = ['hdr'] + ydl_opts["format_sort"]

            if add_thumbnail.value:
                ydl_opts["writethumbnail"] = True
                if not any(p.get("key") == "EmbedThumbnail" for p in ydl_opts["postprocessors"]):
                    ydl_opts["postprocessors"].append({"key": "EmbedThumbnail", "already_have_thumbnail": False})

        elif ext == "mp3":
            ydl_opts["format_sort"] = []
            ydl_opts["format"] = "bestaudio/best"
            if not any(p.get("key") == "FFmpegExtractAudio" for p in ydl_opts["postprocessors"]):
                ydl_opts["postprocessors"].append({
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3"
                })

            if add_thumbnail.value:
                ydl_opts["writethumbnail"] = True
                if not any(p.get("key") == "EmbedThumbnail" for p in ydl_opts["postprocessors"]):
                    ydl_opts["postprocessors"].append({"key": "EmbedThumbnail", "already_have_thumbnail": False})

            # Set sound quality
            audio_quality_map = {
                "128kbps": "128",
                "192kbps": "192",
                "256kbps": "256",
                "320kbps": "320"
            }
            preferred_quality = audio_quality_map.get(quality)
            if preferred_quality:
                for processor in ydl_opts["postprocessors"]:
                    if processor.get("key") == "FFmpegExtractAudio" and processor.get("preferredcodec") == "mp3":
                        processor["preferredquality"] = preferred_quality

        elif ext == "m4a":
            ydl_opts["format_sort"] = []
            ydl_opts["format"] = "bestaudio/best"
            if not any(p.get("key") == "FFmpegExtractAudio" for p in ydl_opts["postprocessors"]):
                ydl_opts["postprocessors"].append({
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a"
                })

            if add_thumbnail.value:
                ydl_opts["writethumbnail"] = True
                if not any(p.get("key") == "EmbedThumbnail" for p in ydl_opts["postprocessors"]):
                    ydl_opts["postprocessors"].append({"key": "EmbedThumbnail", "already_have_thumbnail": False})

            # Set sound quality
            audio_quality_map = {
                "128kbps": "128",
                "192kbps": "192",
                "256kbps": "256",
                "320kbps": "320"
            }
            preferred_quality = audio_quality_map.get(quality)
            if preferred_quality:
                for processor in ydl_opts["postprocessors"]:
                    if processor.get("key") == "FFmpegExtractAudio" and processor.get("preferredcodec") == "mp3":
                        processor["preferredquality"] = preferred_quality

        elif ext == "wav":
            ydl_opts["format_sort"] = []
            ydl_opts["format"] = "bestaudio/best"
            if not any(p.get("key") == "FFmpegExtractAudio" for p in ydl_opts["postprocessors"]):
                ydl_opts["postprocessors"].append({
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav"
                })

        elif ext == "opus":
            ydl_opts["format_sort"] = []
            ydl_opts["format"] = "bestaudio/best"
            if not any(p.get("key") == "FFmpegExtractAudio" for p in ydl_opts["postprocessors"]):
                ydl_opts["postprocessors"].append({
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "opus"
                })
            if add_thumbnail.value:
                ydl_opts["writethumbnail"] = True
                if not any(p.get("key") == "EmbedThumbnail" for p in ydl_opts["postprocessors"]):
                    ydl_opts["postprocessors"].append({"key": "EmbedThumbnail", "already_have_thumbnail": False})

        elif ext == "flac":
            ydl_opts["format_sort"] = []
            ydl_opts["format"] = "bestaudio/best"
            if not any(p.get("key") == "FFmpegExtractAudio" for p in ydl_opts["postprocessors"]):
                ydl_opts["postprocessors"].append({
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "flac"
                })
            if add_thumbnail.value:
                ydl_opts["writethumbnail"] = True
                if not any(p.get("key") == "EmbedThumbnail" for p in ydl_opts["postprocessors"]):
                    ydl_opts["postprocessors"].append({"key": "EmbedThumbnail", "already_have_thumbnail": False})

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                now_title.value = t("no_file_processing")
                now_title.update()
                status_text.value = t("download_complete")
                status_text.update()
                progress_bar.value = 1
                progress_bar.update()

        except Exception as ex:
            status_text.value = t("error_prefix") + remove_ansi_codes(str(ex))
            status_text.update()
            progress_bar.value = 0
            progress_bar.update()

        finally:
            dl_btn.disabled = False
            dl_btn.text = t("download_button")
            dl_btn.icon = Icons.DOWNLOAD
            dl_btn.update()
            now_title.label = t("processing_file_label")
            now_title.update()


    outpath_dialog = FilePicker(on_result=sel_path)
    cookie_dialog = FilePicker(on_result=sel_cookie)

    page.overlay.extend([outpath_dialog,cookie_dialog])

    def change_language(e):
        """Change language and redraw UI"""
        load_locale(language_selector.value)
        # Redraw each UI element
        url_input.label = t("url_label")
        url_input.hint_text = t("url_hint")
        url_input.tooltip = t("url_tooltip")
        outpath_input.label = t("save_path_label")
        outpath_btn.text = t("select_button")
        cookie_btn.text = t("select_button")
        now_title.label = t("processing_file_label")
        now_title.value = t("no_file_processing")
        ext_sel.label = t("extension_label")
        ext_sel.options[-1].text = t("thumbnail")
        quality_sel.label = t("quality_label")
        playlist.label = t("playlist_title_switch")
        playlist_index.label = t("playlist_index_switch")
        add_thumbnail.label = t("add_thumbnail_switch")
        cookie_input.label = t("cookie_label")
        status_text.value = t("progress_text")
        dl_btn.text = t("download_button")
        enable_hdr.label = t("enable_hdr")
        use_aria2c.label = t("use_aria2c")
        page.appbar.actions.clear()
        page.appbar.actions = [
            IconButton(
                icon=Icons.INFO,
                on_click=open_about_dialog
            ),
            IconButton(
                icon=Icons.REFRESH,
                on_click=lambda _:w_init()
            )
        ]
        about_dialog.title = Text(t("about_title"))
        about_dialog.content = Column([
            Text(t("about_text").format(version=get_version())),
        ])
        about_dialog.actions = [
            TextButton(t("close"),on_click=close_about_dialog)
        ]
        page.update()

    # UI elements
    url_input = TextField(
        label=t("url_label"),
        hint_text=t("url_hint"),
        tooltip=t("url_tooltip"),
        on_submit=download
    )
    dl_btn = FloatingActionButton(
        text=t("download_button"),
        icon=Icons.DOWNLOAD,
        on_click=download
    )
    outpath_input = TextField(
        value=outpath,
        label=t("save_path_label"),
        expand=True,
        read_only=True
    )
    outpath_btn = TextButton(
        text=t("select_button"),
        icon=Icons.FOLDER,
        on_click=lambda _: outpath_dialog.get_directory_path(dialog_title=t("select_save_path"))
    )
    now_title = TextField(
        label=t("processing_file_label"),
        read_only=True,
        value=t("no_file_processing")
    )
    progress_bar = ProgressBar(value=0)
    ext_sel = Dropdown(
        label=t("extension_label"),
        options=[
            dropdown.Option(key="mp4", text="MP4"),
            dropdown.Option(key="mp3", text="MP3"),
            dropdown.Option(key="m4a", text="M4A"),
            dropdown.Option(key="wav", text="WAV"),
            dropdown.Option(key="opus", text="OPUS"),
            dropdown.Option(key="flac", text="FLAC"),
            dropdown.Option(key="thumbnail", text=t("thumbnail")),
        ],
        expand=True,
        on_change=change_ext,
        value="mp4"
    )
    quality_sel = Dropdown(
        label=t("quality_label"),
        expand=True,
        options=mp4_qualitys,
        value=mp4_qualitys[0].key
    )
    playlist = Switch(label=t("playlist_title_switch"))
    playlist_index = Switch(label=t("playlist_index_switch"))
    cookie_input = TextField(
        label=t("cookie_label"),
        expand=True,
        read_only=True
    )
    add_thumbnail = Switch(label=t("add_thumbnail_switch"))
    cookie_btn = TextButton(
        text=t("select_button"),
        icon=Icons.COOKIE,
        on_click=lambda _: cookie_dialog.pick_files(allow_multiple=False, allowed_extensions=["txt"])
    )
    status_text = Text(value=t("progress_text"))
    enable_hdr = Switch(label=t("enable_hdr"))
    use_aria2c = Switch(label=t("use_aria2c"))

    # Added Dropdown for language selection
    language_selector = Dropdown(
        label="Language",
        options=[
            dropdown.Option(key="ja", text="日本語"),
            dropdown.Option(key="en", text="English"),
            dropdown.Option(key="zh-cn", text="简体中文")
        ],
        value=current_locale,
        on_change=change_language
    )

    # layout
    page.add(
        language_selector,
        url_input,
        Row([outpath_input, outpath_btn]),
        dl_btn,
        Row([ext_sel, quality_sel]),
        playlist,
        playlist_index,
        enable_hdr,
        add_thumbnail,
        use_aria2c,
        Row([cookie_input, cookie_btn]),
        now_title,
        progress_bar,
        status_text
    )


app(target=main)
