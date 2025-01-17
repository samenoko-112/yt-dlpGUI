from flet import *
from yt_dlp import YoutubeDL
import re
import os
import json
import sys

# 現在の言語を保持
current_locale = "ja"
translations = {}

def resource_path(relative_path):
    """PyInstaller 対応のリソースパス取得"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)  # PyInstaller の一時ディレクトリ
    return os.path.join(os.path.abspath("."), relative_path)

def load_locale(locale: str):
    """指定された言語の翻訳を読み込む"""
    global translations, current_locale
    current_locale = locale
    try:
        # 修正: リソースパスから読み込む
        locale_path = resource_path(f"locale/{locale}.json")
        with open(locale_path, "r", encoding="utf-8") as f:
            translations = json.load(f)
    except FileNotFoundError:
        print(f"Error: locale/{locale}.json が見つかりません")
        translations = {}

def t(key: str) -> str:
    """翻訳キーを取得"""
    return translations.get(key, key)

load_locale(current_locale)

outpath = os.path.expanduser('~') + "/ytdlp"
cookie = None

mp4_qualitys = [dropdown.Option(key="Auto"), dropdown.Option(key="144p"), dropdown.Option(key="240p"), dropdown.Option(key="360p"), dropdown.Option(key="480p"), dropdown.Option(key="720p"), dropdown.Option(key="1080p")]
mp3_qualitys = [dropdown.Option(key="Auto"), dropdown.Option(key="128kbps"), dropdown.Option(key="192kbps"), dropdown.Option(key="256kbps"), dropdown.Option(key="320kbps")]

def main(page: Page):
    page.title = "yt-dlpGUI"
    page.window.width = 500
    page.padding = 16
    page.fonts = {
        "KosugiMaru": "fonts/KosugiMaru-Regular.ttf"
    }
    page.theme = Theme(font_family="KosugiMaru")

    def change_ext(e):
        if ext_sel.value == "mp4":
            quality_sel.options = mp4_qualitys
            quality_sel.value = mp4_qualitys[0].key
        elif ext_sel.value == "mp3":
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
        outpath_input.value = outpath
        outpath_input.update()
    
    def sel_cookie(e: FilePickerResultEvent):
        global cookie
        if e.files:
            cookie = e.files[0].path
        else:
            cookie = ""
        cookie_input.value = cookie
        cookie_input.update()

    # ANSIコードを削除する関数
    def remove_ansi_codes(text):
        return re.sub(r'\x1b\[[0-9;]*m', '', text)

    # ダウンロード関数
    def download(e):
        # ダウンロードボタンを「ダウンロード中」に設定
        dl_btn.disabled = True
        dl_btn.text = t("download_in_progress")
        dl_btn.icon = Icons.DOWNLOADING
        dl_btn.update()

        # プログレスバーとステータスを初期化
        progress_bar.value = None
        progress_bar.update()
        status_text.value = t("status_starting")
        status_text.update()

        # yt-dlp のフック関数
        def hook(d):
            progress_bar.value = None
            progress_bar.update()
            status_text.value = t("status_processing")
            status_text.update()

            if d["status"] == "downloading":
                # 進捗をパーセントからバーに変換
                progress = remove_ansi_codes(d.get("_percent_str", "0%"))
                progress = progress.strip('%')
                try:
                    progress_float = float(progress)
                    progress_bar.value = progress_float / 100
                    progress_bar.update()
                except ValueError:
                    pass

                # その他の進捗情報を表示
                speed = remove_ansi_codes(d.get("_speed_str", t("unknown")))
                eta = remove_ansi_codes(d.get("_eta_str", t("unknown")))

                status_text.value = t("status_progress").format(progress=progress, speed=speed, eta=eta)
                status_text.update()

                title = remove_ansi_codes(d.get("filename"))
                now_title.value = title.replace(outpath, "")
                now_title.update()

            elif d["status"] == "postprocessing":
                progress_bar.value = None
                progress_bar.update()
                status_text.value = t("status_postprocessing")
                status_text.update()

        url = url_input.value
        quality = quality_sel.value
        ext = ext_sel.value

        ydl_opts = {
            "outtmpl": f"{outpath}/%(title)s.%(ext)s",
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "progress_hooks": [hook],
            "postprocessors": [
                {
                    "key": "FFmpegMetadata",
                    "add_metadata": True
                }
            ],
            "quiet": False,
            "ignoreerrors": True,
            "default_search": "ytsearch"
        }

        # Cookieファイルの設定
        if cookie_input.value:
            ydl_opts["cookiefile"] = cookie

        # サムネイルの設定
        if ext == t("thumbnail"):
            ydl_opts["writethumbnail"] = True
            ydl_opts["skip_download"] = True
            ydl_opts["outtmpl"] = f"{outpath}/%(title)s.%(ext)s"

        # プレイリストのタイトルでフォルダを作成
        if playlist.value:
            ydl_opts["outtmpl"] = f"{outpath}/%(playlist_title)s/%(title)s.%(ext)s"

        # プレイリストのインデックスをファイル名に追加
        if playlist_index.value:
            ydl_opts["outtmpl"] = f"{outpath}/%(playlist_index)02d - %(title)s.%(ext)s" if not playlist.value else f"{outpath}/%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s"

        # フォーマットの設定
        if ext == "mp4":
            quality_formats = {
                "Auto": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "144p": "bestvideo[height<=144][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "240p": "bestvideo[height<=240][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            }
            ydl_opts["format"] = quality_formats.get(quality, quality_formats["Auto"])

            if add_samune.value:
                ydl_opts["writethumbnail"] = True
                if not any(p.get("key") == "EmbedThumbnail" for p in ydl_opts["postprocessors"]):
                    ydl_opts["postprocessors"].append({"key": "EmbedThumbnail", "already_have_thumbnail": False})

        elif ext == "mp3":
            ydl_opts["format"] = "bestaudio/best"
            if not any(p.get("key") == "FFmpegExtractAudio" for p in ydl_opts["postprocessors"]):
                ydl_opts["postprocessors"].append({
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3"
                })

            if add_samune.value:
                ydl_opts["writethumbnail"] = True
                if not any(p.get("key") == "EmbedThumbnail" for p in ydl_opts["postprocessors"]):
                    ydl_opts["postprocessors"].append({"key": "EmbedThumbnail", "already_have_thumbnail": False})

            # 音質を設定
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

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                ydl.download([info["webpage_url"]])
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
        """言語を変更し、UIを再描画する"""
        load_locale(language_selector.value)
        # 各UI要素を再描画
        url_input.label = t("url_label")
        url_input.hint_text = t("url_hint")
        url_input.tooltip = t("url_tooltip")
        outpath_input.label = t("save_path_label")
        now_title.label = t("processing_file_label")
        ext_sel.label = t("extension_label")
        quality_sel.label = t("quality_label")
        playlist.label = t("playlist_title_switch")
        playlist_index.label = t("playlist_index_switch")
        add_samune.label = t("add_thumbnail_switch")
        cookie_input.label = t("cookie_label")
        status_text.value = t("progress_text")
        dl_btn.text = t("download_button")
        page.update()

    # UI要素
    url_input = TextField(
        label=t("url_label"),
        hint_text=t("url_hint"),
        tooltip=t("url_tooltip")
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
            dropdown.Option(key="thumbnail", text=t("thumbnail"))
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
    add_samune = Switch(label=t("add_thumbnail_switch"))
    cookie_btn = TextButton(
        text=t("select_button"),
        icon=Icons.COOKIE,
        on_click=lambda _: cookie_dialog.pick_files(allow_multiple=False, allowed_extensions=["txt"])
    )
    status_text = Text(value=t("progress_text"))

    # 言語選択用のDropdownを追加
    language_selector = Dropdown(
        label="Language",
        options=[
            dropdown.Option(key="ja", text="日本語"),
            dropdown.Option(key="en", text="English")
        ],
        value=current_locale,
        on_change=change_language
    )

    # レイアウト
    page.add(
        language_selector,
        url_input,
        Row([outpath_input, outpath_btn]),
        dl_btn,
        Row([ext_sel, quality_sel]),
        playlist,
        playlist_index,
        add_samune,
        Row([cookie_input, cookie_btn]),
        now_title,
        progress_bar,
        status_text
    )


app(target=main, assets_dir="assets")
