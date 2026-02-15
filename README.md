phone2avif (スマホ写真圧縮くん) v1.62
Googleフォトの容量制限に立ち向かう。思い出の質を落とさず、データ量を1/10以下へ。

phone2avif は、スマホ（iPhone/Android）で撮影した大量の写真（JPG, PNG, HEICなど）を、次世代画像フォーマット AVIF に一括変換・最適化するデスクトップツールです。

✨ 特徴
圧倒的な圧縮率: AVIFフォーマットを採用。JPEG比で最大90%以上のファイルサイズ削減を目指しつつ、見た目の美しさを維持します。

iPhone (HEIC) 完全対応: iPhone特有のHEIC形式も直接読み込み可能。

Exif情報の完全移植: ExifTool を使用し、撮影日時やGPS情報、カメラモデルなどのメタデータを1ビットも欠かさず移行。Googleフォトにアップロードしてもタイムラインが崩れません。

並列高速処理: CPUのマルチコアをフル活用。数万枚のアーカイブも短時間で処理します。

簡単操作: フォルダをドラッグ＆ドロップしてボタンを押すだけ。

🚀 使い方
ダウンロード: Releases から最新のZipファイルをダウンロードして解凍します。

実行: phone2avif.exe を起動します。

注意: 同一フォルダに avifenc.exe と exiftool.exe があることを確認してください。

フォルダ指定: 変換したい写真が入ったフォルダをアプリへドラッグ＆ドロップします。

設定: 目標サイズ（推奨: 100KB〜150KB）または固定クオリティを選択します。

開始: 「一括変換を開始する」をクリック。あとは待つだけです！

🛠 インストール・ビルド
開発者自身でビルドする場合、以下のライブラリが必要です。

Bash
pip install Pillow pillow-heif tkinterdnd2 pyinstaller
EXE化コマンド：

Bash
pyinstaller --noconsole --onefile --collect-all tkinterdnd2 --collect-all pillow_heif --name phone2avif conv.py
⚖️ ライセンス
phone2avif: MIT License

内部で使用している外部ツール:

avifenc (libavif): BSD 2-Clause License

ExifTool (by Phil Harvey): Perl Artistic / GPL

詳細は同梱の LICENSE_TOOLS.txt を参照してください。
