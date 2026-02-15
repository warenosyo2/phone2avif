スマホ写真圧縮くん v1.77

スマホ写真圧縮くんは、スマホ（iPhone/Android）で撮影した大量の写真（JPG, PNG, HEICなど）やPCで撮ったスクショなどを、次世代画像フォーマット AVIF に一括変換・最適化するWindows用ツールです。スマホの写真をGoogle Photosにそのままアップロードしていくと、圧縮モード（容量セーブモード, Storage saver）でも1Mbyteとか結構な容量を食います。たまに5Mbyteとか食っているケースも。本ツールを使えば圧縮効率が高く、画質劣化しにくい最新のAVIFフォーマットでの圧縮・リサイズが可能で、Google Photosの無料容量15Gbyteの範囲で10万枚保存してもスマホ画面で見せるぶんにはいいかんじの画質をキープできます。

おすすめサイズと容量はサイズ1920(長辺が1920)でサイズ指定が100kb、これならまぁスマホ画面ならOKかなというレベルになるはずです。

注意点

Google PhotosのPC用一括転送ツールつまりGoogle DriveのSyncツールですが、avifを画像ファイルとして認識しません(2026/2/15時点)　そのため、**必ずWeb版のGoogle Photos（Googleフォト）にドラッグアンドドロップしてのアップロードが必要です。**これならavifをそのまま認識します。

加えて、アップロード時にStorage Saver（日本語だと　保存容量の節約）を選んではダメです。せっかくAVIFにまでして画質チューンした圧縮版を、さらに圧縮しようとしたりして逆に容量が増えたりします。画質が悪化することも。なので、必ずアップロード時は「Original Quality」（日本語だと　元の画質）でアップロードするようにしてください。

✨ 特徴 圧倒的な圧縮率: AVIFフォーマットを採用。JPEG比で最大90%以上のファイルサイズ削減を目指しつつ、見た目の美しさを維持します。 iPhone (HEIC) 完全対応: iPhone特有のHEIC形式も直接読み込み可能。 Exif情報の完全移植: ExifTool を使用し、撮影日時やGPS情報、カメラモデルなどのメタデータを1ビットも欠かさず移行。Googleフォトにアップロードしてもタイムラインが崩れません。 並列高速処理: CPUのマルチコアをフル活用。数万枚のアーカイブも短時間で処理します。 簡単操作: フォルダをドラッグ＆ドロップしてボタンを押すだけ。

🚀 使い方 ダウンロード: Releases から最新のZipファイルをダウンロードして解凍します。同梱されている avifenc.exe と exiftool.exe は必ずそのまま解凍し、スマホ写真圧縮くん.exeと同一フォルダに置いてください。 実行: スマホ写真圧縮くん.exe を起動します。 フォルダ指定: 変換したい写真が入ったフォルダをアプリへドラッグ＆ドロップします。 設定: 目標サイズ（推奨: 100KB〜150KB）または固定クオリティを選択します。 開始: 「一括変換を開始する」をクリック。あとは待つだけです！

🛠 インストール・ビルド 開発者自身でビルドする場合、以下のライブラリが必要です。

Bash pip install Pillow pillow-heif tkinterdnd2 pyinstaller EXE化コマンド：

Bash pyinstaller --noconsole --onefile --collect-all tkinterdnd2 --collect-all pillow_heif --name phone2avif conv.py ⚖️ ライセンス スマホ写真圧縮くん: MIT License

内部で使用している外部ツール:

avifenc (libavif): BSD 2-Clause License ExifTool (by Phil Harvey): Perl Artistic / GPL
