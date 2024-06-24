from flet import (
    Page,Text,ElevatedButton,FloatingActionButton,TextField,Dropdown,dropdown,Switch,FilePicker,FilePickerResultEvent
)
import flet as ft
import time
import os
import subprocess

version = 1.11

process_running = False
current_process = None

dl_log = "実行時のログ"
cookie_file = ""
home = os.path.expanduser('~')
output_path = home+"/yt-dlp"

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
    
    def download(e):
        global dl_log
        global process_running
        global current_process

        if process_running == True:
            if current_process:
                current_process.terminate()
            process_running = False
            return

        url = url_input.value
        dl_log = "実行時のログ"
        command = ['yt-dlp','--add-metadata','--newline',"--progress-template","download:[Progress]%(progress._percent_str)s"]
        if url != "":
            command.append(url)
            if mode_sel.value == "mp4":
                command.extend(['--merge-output-format','mp4'])
                command.append('-f')
                if quality_sel.value == "Auto":
                    command.append('bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]')
                elif quality_sel.value == "1080p":
                    command.append('bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]')
                elif quality_sel.value == "720p":
                    command.append('bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]')
                elif quality_sel.value == "480p":
                    command.append('bestvideo[ext=mp4][height<=480]+bestaudio[ext=m4a]/best[ext=mp4][height<=480]')
                elif quality_sel.value == "360p":
                    command.append('bestvideo[ext=mp4][height<=360]+bestaudio[ext=m4a]/best[ext=mp4][height<=360]')
                elif quality_sel.value == "240p":
                    command.append('bestvideo[ext=mp4][height<=240]+bestaudio[ext=m4a]/best[ext=mp4][height<=240]')
                elif quality_sel.value == "144p":
                    command.append('bestvideo[ext=mp4][height<=144]+bestaudio[ext=m4a]/best[ext=mp4][height<=144]')
            elif mode_sel.value == "mp3":
                command.extend(['-f','bestaudio/best','-x'])
                if quality_sel.value == "Auto":
                    command.extend(['--audio-format', 'mp3'])
                elif quality_sel.value == "320kbps":
                    command.extend(['--audio-format', 'mp3', '--audio-quality', '320K'])
                elif quality_sel.value == "128kbps":
                    command.extend(['--audio-format', 'mp3', '--audio-quality', '128K'])
            elif mode_sel.value == "wav":
                command.append('-f')
                command.append('bestaudio')
                command.append('-x')
                command.append('--audio-format')
                command.append('wav')
            if use_multi.value == True:
                command.extend(['-N',f'{int(multi_threads.value)}'])
            else:
                pass
            if playlist.value == True and name_index.value == False:
                command.extend(['-o',f'{output_path}/%(playlist_title)s/%(title)s.%(ext)s'])
            elif playlist.value == True and name_index.value == True:
                command.extend(['-o',f'{output_path}/%(playlist_title)s/%(playlist_index)s_%(title)s.%(ext)s'])
            elif playlist.value == False and name_index.value == False:
                command.extend(['-o',f'{output_path}/%(title)s.%(ext)s'])
            elif playlist.value == False and name_index.value == True:
                command.extend(['-o',f'{output_path}/%(playlist_index)s_%(title)s.%(ext)s'])
            if use_aria2.value == True:
                command.extend(["--external-downloader", "aria2c", "--external-downloader-args", "-x 16 -s 16"])
            else:
                pass
            if emb_thumbnail.value == True:
                command.extend(['--embed-thumbnail'])
            else:
                pass
            if cookie_file:
                command.extend(['--cookies', cookie_input.value])
            print(command)
            dl_btn.text = "ダウンロード中"
            dl_btn.update()

            process_running = True

            with open("dl.log","w",encoding="shift-jis") as log_file:

                try:

                    with subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,encoding="shift-jis") as process:

                        current_process = process

                        for line in process.stdout:
                            if line.startswith("[Progress]"):
                                progress_str = line.split("[Progress]")[1].split("%")[0].strip()
                                progress_value = float(progress_str) / 100
                                progress_bar.value = progress_value
                                progress_bar.update()
                            else:
                                progress_bar.value = None
                                progress_bar.update()
                                log_out.value = line
                                log_out.update()
                                log_file.write(line)

                        process.wait()

                        if process.returncode == 0:
                            progress_bar.value = 1
                            progress_bar.update()
                            log_out.value = "正常にダウンロードできました"
                            log_out.update()
                            log_file.write(f"{'-'*50} 処理ここまで {'-'*50}\n")
                            dl_btn.text = "ダウンロード"
                            dl_btn.update()
                            return
                        else:
                            progress_bar.value = 0
                            progress_bar.update()
                            log_out.value = "エラーが発生しました"
                            log_out.update()
                            log_file.write(f"{'-'*50} 処理ここまで {'-'*50}\n")
                            dl_btn.text = "ダウンロード"
                            dl_btn.update()
                            return
                except Exception as e:
                    progress_bar.value = 0
                    progress_bar.update()
                    log_out.value = "中断しました"
                    log_out.update()
                    log_file.write(f"{'-'*50} 処理ここまで {'-'*50}\n")
                    dl_btn.text = "ダウンロード"
                    dl_btn.update()
                    return
                
                finally:
                    process_running = False
                    current_process = None
                    return

    
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
        Text("yt-dlpGUI",size=20),
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
