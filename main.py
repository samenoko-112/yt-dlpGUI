from flet import (
    Page,Text,ElevatedButton,FloatingActionButton,TextField,Dropdown,dropdown,Switch,FilePicker,FilePickerResultEvent
)
import flet as ft
import os
import subprocess
from plyer import notification
#import winsound

def main(page:Page):
    page.title = "yt-dlpGUI ver:0.1b"
    page.window_width = 550
    page.padding = 16
    home = os.path.expanduser('~')
    output_path = home+"/yt-dlp"
    dl_log = "実行時のログ"

    def sel_path(e: FilePickerResultEvent):
        nonlocal output_path
        before = output_path
        output_path = e.path if e.path else before
        path_input.value = output_path
        path_input.update()
        return
    
    def download(e):
        nonlocal dl_log
        url = url_input.value
        dl_log = "実行時のログ"
        command = ['yt-dlp','--add-metadata']
        if url != "":
            command.append(url)
            if mode_sel.value == "mp4":
                command.append('-f')
                command.append('bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]')
            elif mode_sel.value == "mp3":
                command.append('-f')
                command.append('bestaudio')
                command.append('-x')
                command.append('--audio-format')
                command.append('mp3')
                command.append('--audio-quality')
                command.append('256K')
            elif mode_sel.value == "wav":
                command.append('-f')
                command.append('bestaudio')
                command.append('-x')
                command.append('--audio-format')
                command.append('wav')
            if use_multi.value == True:
                command.extend(['-N','8'])
            else:
                pass
            if playlist.value == True:
                command.extend(['-o',f'{output_path}/%(playlist_title)s/%(title)s.%(ext)s'])
            else:
                command.extend(['-o',f'{output_path}/%(title)s.%(ext)s'])
            if use_aria2.value == True:
                command.extend(["--external-downloader", "aria2c", "--external-downloader-args", "-x 16 -s 16"])
            else:
                pass
            if emb_thumbnail.value == True:
                command.extend(['--embed-thumbnail'])
            else:
                pass

            with open("dl.log","a") as log_file:

                with subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as process:

                    dl_btn.text = "ダウンロード中"
                    dl_btn.disabled = True
                    dl_btn.update()

                    for line in process.stdout:
                        log_out.value = line
                        log_out.update()
                        log_file.write(line)
                    process.wait()
                    if process.returncode == 0:
                        dl_log = "正常に終了!!"
                        log_out.value = dl_log
                        log_out.update()
                        dl_btn.text = "ダウンロード"
                        dl_btn.disabled = False
                        dl_btn.update()
                        #winsound.MessageBeep(winsound.MB_OK)
                        log_file.write(f"{'-'*50} 処理ここまで {'-'*50}\n")
                        return
                    else:
                        dl_log = "エラーが発生したってよ"
                        log_out.value = dl_log
                        log_out.update()
                        dl_btn.text = "ダウンロード"
                        dl_btn.disabled = False
                        dl_btn.update()
                        #winsound.MessageBeep(winsound.MB_ICONHAND)
                        log_file.write(f"{'-'*50} 処理ここまで {'-'*50}\n")
                        return
                    

    
    dir_dialog = FilePicker(on_result=sel_path)

    page.overlay.extend([dir_dialog])

    url_input = TextField(hint_text="URLを入力",label="URL",icon=ft.icons.MOVIE)
    path_input = TextField(value=output_path,hint_text="保存先を選択",label="保存先",icon=ft.icons.FOLDER,expand=True,read_only=True)
    path_btn = ft.TextButton("選択",icon=ft.icons.FOLDER_COPY,on_click=lambda _:dir_dialog.get_directory_path())
    dl_btn = FloatingActionButton("ダウンロード",icon=ft.icons.DOWNLOAD,on_click=download)
    mode_sel = Dropdown(value="mp4",label="フォーマット",options=[dropdown.Option("mp4"),dropdown.Option("mp3"),dropdown.Option("wav")])
    log_out = Text(value=dl_log,max_lines=5,)
    use_multi = Switch(label="同時接続する",tooltip=f"同時接続して高速でダウンロードできるようにします\nエラーが発生する可能性があります",expand=True)
    emb_thumbnail = Switch(label="サムネイルを埋め込む",tooltip=f"ファイルにサムネイルを埋め込みます")
    playlist = Switch(label="プレイリスト名でフォルダを作成",tooltip=f"プレイリストの名前でフォルダを作成し、その中にファイルを保存します\nプレイリストでない場合はNAに保存されます")
    use_aria2 = Switch(label="Aria2を使う",tooltip=f"外部ダウンローダーであるAria2を使用します。\n同時接続数を増やし高速でダウンロードできるようにします\n接続が制限され極端に速度が低下する可能性があります",expand=True)

    page.add(
        Text("yt-dlpGUI",size=20),
        url_input,
        ft.Row([path_input,path_btn]),
        Text("オプション",size=18),
        mode_sel,
        playlist,
        emb_thumbnail,
        ft.Row([use_multi,use_aria2]),
        Text("ログ",size=18),
        log_out,
        dl_btn
    )

ft.app(main)
