import os
import urllib.request
import zipfile
import shutil

# BtbN FFmpegの「shared」バージョンのURLを取得（Windows専用）
def get_ffmpeg_url():
    return "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"

# zipファイルを展開し、展開されたフォルダパスを返す
def extract_archive(zip_file, extract_path):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
        # 展開されたディレクトリのリストを取得
        return [name for name in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, name))]

# FFmpegのダウンロードと解凍
def download_and_extract_ffmpeg():
    # ダウンロード先のURLを取得
    ffmpeg_url = get_ffmpeg_url()
    
    # ファイル名を取得
    file_name = ffmpeg_url.split("/")[-1]
    
    # 保存先のパス（プログラムと同じディレクトリ）
    download_path = os.path.join(os.getcwd(), file_name)
    
    # ダウンロード処理
    print(f"Downloading FFmpeg from {ffmpeg_url}...")
    urllib.request.urlretrieve(ffmpeg_url, download_path)
    print("Download complete!")
    
    # 一時展開先のディレクトリ
    temp_extract_path = os.path.join(os.getcwd(), "temp_ffmpeg")
    os.makedirs(temp_extract_path, exist_ok=True)
    
    # アーカイブを展開して、展開されたトップディレクトリを取得
    extracted_folders = extract_archive(download_path, temp_extract_path)
    
    if extracted_folders:
        # 最初の展開フォルダのbinディレクトリを指定
        extracted_bin_path = os.path.join(temp_extract_path, extracted_folders[0], "bin")
        if os.path.exists(extracted_bin_path):
            # binフォルダ内のファイルをカレントディレクトリに移動
            for item in os.listdir(extracted_bin_path):
                s = os.path.join(extracted_bin_path, item)
                d = os.path.join(os.getcwd(), item)
                if os.path.isdir(s):
                    shutil.move(s, d)
                else:
                    shutil.copy2(s, d)
            print(f"FFmpeg bin contents extracted to {os.getcwd()}")
        else:
            print("Error: bin folder not found in the extracted files.")
    else:
        print("Error: No extracted folders found.")
    
    # 一時展開先の削除
    shutil.rmtree(temp_extract_path)
    
    # ダウンロードしたファイルの削除
    os.remove(download_path)