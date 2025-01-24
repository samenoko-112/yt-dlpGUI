# yt-dlpGUI

> [!CAUTION]
> モチベーションが切れたため一度開発を止めさせていただきます。
> 気が向いたときにまた再開するかもしれません。

This is the Japanese version of the README. For the English version, click here → [en](README.en.md)

## 概要
yt-dlpをGUIで使いやすくしたやつです。  
私が使うために作られたやつをいい感じにいい感じにしたやつです。

## 動作に必要なソフトウェア
- ffmpeg

> Windows環境でのインストール
> ```bash:ターミナル
> winget install Gyan.FFmpeg
> ```

## 主な機能
### 検索機能
URLを入れなくても検索ワードを入れると一番上の結果をダウンロードします。

### 形式・品質の選択
形式はmp4,mp3,m4a,wav,opus,flac,サムネイルから選ぶことができます。  
品質はmp4の場合、自動,144pから2160pまで選択可能。mp3,m4aの場合は自動,128kbpsから320kbpsまで4段階で選択可能です。

### プレイリスト云々
プレイリストのタイトルでフォルダを作成してその中に保存したり、  
ファイル名にプレイリストのインデックスをファイル名に追加したりってのができます。  

### サムネイルを追加
ファイルにサムネイルを埋め込んでくれます。  
wav,opusの場合は動作しません。

### Cookieの選択
ブラウザーの拡張機能([Chrome](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc),[Firefox](https://addons.mozilla.org/ja/firefox/addon/cookies-txt/))などを使い取得したcookies.txtを使うことが出来ます。  
cookies.txtを使うことでメンバー限定の動画や要Premiumの動画などをダウンロードすることが出来ます。

### HDRを優先
HDRの動画を優先します。  

### Aria2を使う
外部ダウンローダーである`aria2`を使います。  
一般的により高速になります。

## スクリーンショット

![image](https://github.com/user-attachments/assets/41a929f1-b9e3-497f-afb4-3335e6de8198)

![image](https://github.com/user-attachments/assets/239eef17-f7b3-4133-89bb-ff72e0d44a2e)

## 自分でビルド
pyinstallerを使いビルドできます。

このリポジトリをクローンしてカレントディレクトリを移動、そこで
```bash:
pyinstaller yt-dlpGUI.spec
```

を実行してください。  
`/dist`に保存されます。

## 動作を確認済みのOS
- Microsoft Windows 10.0.19045.5371 (amd64)
- macOS 15.2 (arm64)
- Ubuntu 24.04 (amd64)

Windows以外のOS向けのパッケージの配布はありません。  
動作にはこのリポジトリをクローンしてrequirements.txtに加え、  
ffmpeg、場合によってはlibmpvを導入する必要があります。

## コントリビューター
[@samenoko-112 (開発者)](https://github.com/samenoko-112)  
[@reindex-ot (翻訳)](https://github.com/reindex-ot)
