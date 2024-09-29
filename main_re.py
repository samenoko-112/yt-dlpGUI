from flet import (
    Page,Text,ElevatedButton,FloatingActionButton,TextField,Dropdown,dropdown,Switch,FilePicker,FilePickerResultEvent
)
import flet as ft
import time
import os
from yt_dlp import YoutubeDL
import re
from win11toast import toast

version = 1.2

process_running = False
current_process = None

dl_log = "standby"
cookie_file = ""
home = os.path.expanduser('~')
output_path = home+"/yt-dlp"
title = ""

def main(page:Page):
    page.title = f"yt-dlpGUI ver.{version}"
    page.window.left = 100
    page.window.top = 100
    page.window.width = 550
    page.window.height = 800
    page.padding = 16

    mp4_quality = [dropdown.Option(key="Auto"),dropdown.Option(key="1080p"),dropdown.Option(key="720p"),dropdown.Option(key="480p"),dropdown.Option(key="360p"),dropdown.Option(key="240p"),dropdown.Option(key="144p")]
    mp3_quality = [dropdown.Option(key="Auto"),dropdown.Option(key="320kbps"),dropdown.Option(key="128kbps")]

    def change_options(e):
        if mode_sel.value == "mp4":
            quality_sel.options = mp4_quality
            quality_sel.value = "Auto"
            quality_sel.update()
        elif mode_sel.value == "mp3":
            quality_sel.options = mp3_quality
            quality_sel.value = "Auto"
            quality_sel.update()
        else:
            quality_sel.options = []
            quality_sel.update()

    def sel_path(e: FilePickerResultEvent):
        global output_path
        before = output_path
        output_path = e.path if e.path else before
        path_input.value = output_path
        path_input.update()
        return
    
    def display_multi(e):
        if use_multi.value == True:
            multi_threads.visible = True
            multi_threads.update()
        elif use_multi.value == False:
            multi_threads.visible = False
            multi_threads.update()
    
    def sel_cookie(e: FilePickerResultEvent):
        global cookie_file
        if e.files:
            cookie_file = e.files[0].path
        else:
            cookie_file = ""
        cookie_input.value = cookie_file
        cookie_input.update()
        print(cookie_file)
        return
    
    # ダウンロードの関数部分を書き換え
    def download(e):
        global dl_log
        global process_running
        global current_process
        global title

        if process_running == True:
            process_running = False
            return

        url = url_input.value
        dl_log = "実行時のログ"

        # yt-dlp用のオプションを作成
        ydl_opts = {
            'format': 'best',
            'progress_hooks': [hook],
            'postprocessor_hooks': [post_hook],
            'quiet': False,
            'postprocessors': [
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                }
            ],
            'color': 'no_color'
        }

        ydl_opts['outtmpl'] = f'{output_path}/%(title)s.%(ext)s'

        # モードと品質に基づいてオプションを設定
        if mode_sel.value == "mp4":
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'
            if quality_sel.value == "1080p":
                ydl_opts['format'] = 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]'
            elif quality_sel.value == "720p":
                ydl_opts['format'] = 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]'
            elif quality_sel.value == "480p":
                ydl_opts['format'] = 'bestvideo[ext=mp4][height<=480]+bestaudio[ext=m4a]/best[ext=mp4][height<=480]'
            elif quality_sel.value == "360p":
                ydl_opts['format'] = 'bestvideo[ext=mp4][height<=360]+bestaudio[ext=m4a]/best[ext=mp4][height<=360]'
            elif quality_sel.value == "240p":
                ydl_opts['format'] = 'bestvideo[ext=mp4][height<=240]+bestaudio[ext=m4a]/best[ext=mp4][height<=240]'
            elif quality_sel.value == "144p":
                ydl_opts['format'] = 'bestvideo[ext=mp4][height<=144]+bestaudio[ext=m4a]/best[ext=mp4][height<=144]'
            
            # サムネイル埋め込みのポストプロセッサ
            if emb_thumbnail.value:
                ydl_opts['writethumbnail'] = True
                ydl_opts.setdefault('postprocessors', []).append({
                    'key': 'EmbedThumbnail',  # mp4にサムネイルを埋め込む
                    'already_have_thumbnail': False,
                })

        elif mode_sel.value == "mp3":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
            # mp3の品質設定
            if quality_sel.value == "320kbps":
                ydl_opts['postprocessors'][0]['preferredquality'] = '320'
            elif quality_sel.value == "128kbps":
                ydl_opts['postprocessors'][0]['preferredquality'] = '128'
            else:
                ydl_opts['postprocessors'][0]['preferredquality'] = '192'  # デフォルトは192kbps
            
            # mp3にサムネイルを埋め込むポストプロセッサ
            if emb_thumbnail.value:
                ydl_opts['writethumbnail'] = True
                ydl_opts['postprocessors'].append({
                    'key': 'EmbedThumbnail',  # mp3にサムネイルを埋め込む
                    'already_have_thumbnail': False,
                })

        elif mode_sel.value == "wav":
            ydl_opts['format'] = 'bestaudio'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }]
            # wavにはサムネイルを無視

        # その他のオプション設定（マルチスレッドなど）
        if use_multi.value:
            ydl_opts['n_threads'] = int(multi_threads.value)

        if playlist.value:
            if name_index.value:
                ydl_opts['outtmpl'] = f'{output_path}/%(playlist_title)s/%(playlist_index)s_%(title)s.%(ext)s'
            else:
                ydl_opts['outtmpl'] = f'{output_path}/%(playlist_title)s/%(title)s.%(ext)s'

        if cookie_file:
            ydl_opts['cookiefile'] = cookie_input.value

        if use_aria2.value:
            ydl_opts['external_downloader'] = 'aria2c'
            ydl_opts['external_downloader_args'] = ['-x', '16', '-s', '16']


        dl_btn.text = "ダウンロード中"
        dl_btn.update()

        process_running = True

        try:
            progress_bar.value = None
            progress_bar.update()
            log_out.value = "開始しています"
            log_out.update()

            # yt-dlpのライブラリを使ってダウンロード
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url,download=False)
                title = info.get('title','None')
                ydl.download([url])
            
            log_out.value = "正常にダウンロードできました"
            log_out.update()
            dl_btn.text = "ダウンロード"
            dl_btn.update()
            progress_bar.value = 1
            progress_bar.update()
            toast("ダウンロード完了",f"{title}のダウンロードが完了しました")

        except Exception as e:
            log_out.value = f"エラーが発生しました: {str(e)}"
            log_out.update()
            dl_btn.text = "ダウンロード"
            dl_btn.update()
            progress_bar.value = 0
            progress_bar.update()
            toast("エラー",f"{e}")

        finally:
            process_running = False

    # プログレスバーの更新用のフック関数
    def hook(d):
        # print(f"Progress: {d['status']}")
        if d['status'] == 'downloading':
            progress = d['_percent_str']
            # ANSIエスケープシーケンスを除去
            progress = re.sub(r'\x1b\[[0-9;]*m', '', progress)
            progress = progress.strip('%')
            try:
                progress_float = float(progress)
                log_out.value = f"{title}をダウンロード中..."
                log_out.update()
                progress_bar.value = progress_float / 100
                progress_bar.update()
            except ValueError:
                log_out.value = f"進捗の変換エラー: {progress}"
                log_out.update()

        elif d['status'] == 'postprocessing':
            progress_bar.value = None
            progress_bar.update()

        elif d['status'] == 'finished':
            progress_bar.value = None
            progress_bar.update()

    def post_hook(d):
        # print(f"Post: {d['status']}")
        log_out.value = "ポストプロセス中"
        log_out.update()

    
    dir_dialog = FilePicker(on_result=sel_path)
    cookie_select = FilePicker(on_result=sel_cookie)

    page.overlay.extend([dir_dialog,cookie_select])

    url_input = TextField(hint_text="URLを入力",label="URL",icon=ft.icons.MOVIE)
    path_input = TextField(value=output_path,hint_text="保存先を選択",label="保存先",icon=ft.icons.FOLDER,expand=True,read_only=True)
    path_btn = ft.TextButton("選択",icon=ft.icons.FOLDER_COPY,on_click=lambda _:dir_dialog.get_directory_path())
    dl_btn = FloatingActionButton("ダウンロード",icon=ft.icons.DOWNLOAD,on_click=download)
    cookie_input = TextField(value=cookie_file, hint_text="Cookieファイルを選択", label="Cookie", icon=ft.icons.COOKIE, expand=True, read_only=True)
    cookie_btn = ft.TextButton("選択", icon=ft.icons.COOKIE, on_click=lambda _:cookie_select.pick_files(allowed_extensions=["txt"]))
    mode_sel = Dropdown(value="mp4",label="フォーマット",options=[dropdown.Option("mp4"),dropdown.Option("mp3"),dropdown.Option("wav")],expand=True,on_change=change_options)
    quality_sel = Dropdown(label="品質",options=mp4_quality,expand=True)
    log_out = Text(value=dl_log,max_lines=1,)
    progress_bar = ft.ProgressBar(value=0)
    name_index = Switch(label="プレイリストのインデックスをファイル名に含める",tooltip=f"ファイル名にプレイリストのインデックスを含めます。")
    use_multi = Switch(label="同時接続する",tooltip=f"同時接続して高速でダウンロードできるようにします\nエラーが発生する可能性があります",expand=True,on_change=display_multi)
    multi_threads = ft.Slider(value=8,max=20,min=1,divisions=20,visible=False,label="{value}")
    emb_thumbnail = Switch(label="サムネイルを埋め込む",tooltip=f"ファイルにサムネイルを埋め込みます")
    playlist = Switch(label="プレイリスト名でフォルダを作成",tooltip=f"プレイリストの名前でフォルダを作成し、その中にファイルを保存します\nプレイリストでない場合はNAに保存されます")
    use_aria2 = Switch(label="Aria2を使う",tooltip=f"外部ダウンローダーであるAria2を使用します。\n同時接続数を増やし高速でダウンロードできるようにします\n接続が制限され極端に速度が低下する可能性があります",expand=True)

    page.add(
        # Text("yt-dlpGUI",size=20),
        url_input,
        ft.Row([path_input,path_btn]),
        Text("オプション",size=18),
        ft.Row([mode_sel,quality_sel]),
        playlist,
        name_index,
        emb_thumbnail,
        ft.Row([use_multi,use_aria2]),
        multi_threads,
        ft.Row([cookie_input, cookie_btn]),
        Text("ログ",size=18),
        log_out,
        progress_bar,
        dl_btn
    )

ft.app(main)
