import os
import subprocess
import threading
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import tkinter.font as tkfont
from PIL import Image, ImageOps
from concurrent.futures import ProcessPoolExecutor
from tkinterdnd2 import DND_FILES, TkinterDnD
import multiprocessing

# --- 外部ツールのパス設定 ---
AVIFENC_PATH = "avifenc.exe"
EXIFTOOL_PATH = "exiftool.exe"

# Windowsで外部プロセス起動時にコンソールウィンドウを表示させないフラグ
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0

def check_external_tools():
    avif_exists = os.path.exists(AVIFENC_PATH)
    exif_exists = os.path.exists(EXIFTOOL_PATH)
    if not avif_exists and not exif_exists:
        messagebox.showerror("エラー", "avifenc.exeとexiftool.exeが見つかりません。同一フォルダに置いてください。")
        sys.exit()
    elif not avif_exists:
        messagebox.showerror("エラー", "avifenc.exeが見つかりません。同一フォルダに置いてください。")
        sys.exit()
    elif not exif_exists:
        messagebox.showerror("エラー", "exiftool.exeが見つかりません。同一フォルダに置いてください。")
        sys.exit()

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

def process_one_image(args):
    input_path, output_path, mode, value, max_long_side = args
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if os.path.exists(output_path): return True
        temp_jpg = f"temp_{os.getpid()}_{os.path.basename(input_path)}.jpg"
        img = Image.open(input_path)
        img = ImageOps.exif_transpose(img)
        w, h = img.size
        scale = max_long_side / max(w, h)
        if scale < 1.0:
            img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        img.convert("RGB").save(temp_jpg, quality=95)
        cmd = [AVIFENC_PATH, "-s", "7", "-j", "1"]
        if mode == 'size':
            cmd += ["--target-size", str(value)]
        else:
            q_val = int(63 - (value * 0.63))
            cmd += ["--min", str(q_val), "--max", str(q_val)]
        cmd += [temp_jpg, output_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
        subprocess.run([EXIFTOOL_PATH, "-overwrite_original", "-TagsFromFile", input_path, "-all:all", output_path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
        if os.path.exists(temp_jpg): os.remove(temp_jpg)
        return True
    except:
        return False

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        check_external_tools()
        # ウィンドウタイトルを正式名称に変更
        self.title("スマホ写真圧縮くん (phone2avif) Ver 1.66")
        self.geometry("750x940")
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except: pass
        self.default_font = tkfont.Font(family="Yu Gothic UI", size=10)
        self.title_font = tkfont.Font(family="Yu Gothic UI", size=11, weight="bold")
        self.option_add("*Font", self.default_font)
        self.input_dirs = []
        self.is_running = False
        self._setup_ui()
        self._toggle_params()

    def _setup_ui(self):
        info_btn = tk.Button(self, text="ℹ アプリについて", command=self.show_license, relief=tk.FLAT, fg="blue")
        info_btn.pack(anchor="e", padx=20, pady=5)
        tk.Label(self, text="1. 処理対象のフォルダを追加（あらゆる画像形式に対応）:", font=self.title_font).pack(pady=(5, 5), anchor="w", padx=20)
        self.list_frame = tk.Frame(self)
        self.list_frame.pack(fill=tk.X, padx=20, pady=5)
        self.listbox = tk.Listbox(self.list_frame, height=8, selectmode=tk.EXTENDED, bg="#fcfcfc")
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.guide_label = tk.Label(self.listbox, text="ここに対象となるフォルダをドラッグアンドドロップしてください", bg="#fcfcfc", fg="gray")
        self.guide_label.place(relx=0.5, rely=0.5, anchor="center")
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind('<<Drop>>', self.on_drop)
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=20)
        tk.Button(btn_frame, text="フォルダを選択して追加", command=self.add_folder, width=20).pack(side=tk.LEFT, pady=5)
        tk.Button(btn_frame, text="選択項目を削除", command=self.remove_folder, width=20).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(self, text="2. 保存先フォルダを指定:", font=self.title_font).pack(pady=(15, 5), anchor="w", padx=20)
        out_frame = tk.Frame(self)
        out_frame.pack(fill=tk.X, padx=20)
        self.entry_output = tk.Entry(out_frame)
        self.entry_output.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)
        tk.Button(out_frame, text="参照", command=self.set_output, width=10).pack(side=tk.LEFT, padx=(5, 0))
        tk.Label(self, text="3. 圧縮設定:", font=self.title_font).pack(pady=(15, 5), anchor="w", padx=20)
        param_container = tk.Frame(self, padx=30)
        param_container.pack(fill=tk.X)
        self.mode_var = tk.StringVar(value="size")
        size_row = tk.Frame(param_container)
        size_row.pack(fill=tk.X, pady=5)
        tk.Radiobutton(size_row, text="目標ファイルサイズ:", variable=self.mode_var, value="size", command=self._toggle_params).pack(side=tk.LEFT)
        self.var_target_size = tk.StringVar(value="100")
        self.entry_size = tk.Entry(size_row, textvariable=self.var_target_size, width=10, justify=tk.RIGHT)
        self.entry_size.pack(side=tk.LEFT, padx=10)
        tk.Label(size_row, text="KB / 枚").pack(side=tk.LEFT)
        qual_row = tk.Frame(param_container)
        qual_row.pack(fill=tk.X, pady=5)
        tk.Radiobutton(qual_row, text="固定クオリティ:", variable=self.mode_var, value="quality", command=self._toggle_params).pack(side=tk.LEFT)
        self.var_quality = tk.StringVar(value="35")
        self.entry_quality = tk.Entry(qual_row, textvariable=self.var_quality, width=10, justify=tk.RIGHT)
        self.entry_quality.pack(side=tk.LEFT, padx=10)
        tk.Label(qual_row, text="(1-100)").pack(side=tk.LEFT)
        ttk.Separator(param_container, orient='horizontal').pack(fill='x', pady=10)
        common_frame = tk.Frame(param_container)
        common_frame.pack(fill=tk.X)
        tk.Label(common_frame, text="リサイズ（長辺）:").grid(row=0, column=0, sticky="w", pady=5)
        self.var_max_side = tk.StringVar(value="1920")
        tk.Entry(common_frame, textvariable=self.var_max_side, width=10, justify=tk.RIGHT).grid(row=0, column=1, padx=10)
        tk.Label(common_frame, text="px").grid(row=0, column=2, sticky="w")
        self.max_sys_cpu = multiprocessing.cpu_count()
        tk.Label(common_frame, text="並列スレッド数:").grid(row=1, column=0, sticky="w", pady=5)
        self.var_threads = tk.StringVar(value=str(max(1, self.max_sys_cpu - 1)))
        tk.Entry(common_frame, textvariable=self.var_threads, width=10, justify=tk.RIGHT).grid(row=1, column=1, padx=10)
        tk.Label(common_frame, text=f"/ システム最大 {self.max_sys_cpu}").grid(row=1, column=2, sticky="w")
        tk.Label(self, text="進捗状況:", font=self.title_font).pack(pady=(20, 5), anchor="w", padx=20)
        self.lbl_counter = tk.Label(self, text="0 / 0 (0%)", font=("Consolas", 12))
        self.lbl_counter.pack()
        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.progress.pack(fill=tk.X, padx=20, pady=10)
        self.lbl_status = tk.Label(self, text="待機中...", fg="#555555")
        self.lbl_status.pack()
        self.action_frame = tk.Frame(self)
        self.action_frame.pack(fill=tk.X, padx=150, pady=20)
        self.btn_start = tk.Button(self.action_frame, text="一括変換を開始する", command=self.start_thread, bg="#28a745", fg="white", font=self.title_font, height=2)
        self.btn_start.pack(fill=tk.X)
        self.btn_stop = tk.Button(self.action_frame, text="変換を中止する", command=self.stop_conversion, bg="#dc3545", fg="white", font=self.title_font, height=2)
        self.btn_stop.pack_forget()

    def show_license(self):
        # アプリ名称を日本語メインに変更
        license_text = (
            "スマホ写真圧縮くん (phone2avif) Ver 1.66\n\n"
            "本アプリはオープンソースとして公開されています。\n"
            "動作には avifenc.exe と exiftool.exe が必要です。\n"
            "詳細は配布パッケージのライセンスファイルを確認してください。"
        )
        messagebox.showinfo("このアプリについて", license_text)

    def on_drop(self, event):
        files = self.splitlist(event.data)
        for f in files:
            path = os.path.normpath(f)
            target = path if os.path.isdir(path) else os.path.dirname(path)
            if target and target not in self.input_dirs:
                self.input_dirs.append(target)
                self.listbox.insert(tk.END, target)
        self._update_guide()

    def _update_guide(self):
        if len(self.input_dirs) > 0: self.guide_label.place_forget()
        else: self.guide_label.place(relx=0.5, rely=0.5, anchor="center")

    def _toggle_params(self):
        if self.mode_var.get() == "size":
            self.entry_size.config(state=tk.NORMAL)
            self.entry_quality.config(state=tk.DISABLED)
        else:
            self.entry_size.config(state=tk.DISABLED)
            self.entry_quality.config(state=tk.NORMAL)

    def add_folder(self):
        path = filedialog.askdirectory()
        if path:
            path = os.path.normpath(path)
            if path not in self.input_dirs:
                self.input_dirs.append(path)
                self.listbox.insert(tk.END, path)
        self._update_guide()

    def remove_folder(self):
        selection = self.listbox.curselection()
        for index in reversed(selection):
            self.input_dirs.pop(index)
            self.listbox.delete(index)
        self._update_guide()

    def set_output(self):
        path = filedialog.askdirectory()
        if path:
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, os.path.normpath(path))

    def start_thread(self):
        if not self.input_dirs or not self.entry_output.get().strip():
            messagebox.showwarning("警告", "設定が不足しています")
            return
        self.is_running = True
        self.btn_start.pack_forget()
        self.btn_stop.pack(fill=tk.X)
        threading.Thread(target=self.run_conversion, daemon=True).start()

    def stop_conversion(self):
        if messagebox.askyesno("確認", "中止しますか？"):
            self.is_running = False
            self.lbl_status.config(text="中止しています...")

    def run_conversion(self):
        output_base = os.path.normpath(self.entry_output.get())
        mode = self.mode_var.get()
        max_side = int(self.var_max_side.get())
        try: num_threads = min(int(self.var_threads.get()), self.max_sys_cpu, 61)
        except: num_threads = self.max_sys_cpu - 1
        val = int(self.var_target_size.get()) * 1024 if mode == "size" else int(self.var_quality.get())
        
        tasks = []
        self.lbl_status.config(text="ファイルをスキャン中...")
        self.update_idletasks()
        valid_exts = ('.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.bmp', '.tif', '.tiff', '.ico', '.avif')
        for input_base in self.input_dirs:
            folder_name = os.path.basename(input_base)
            for root, _, files in os.walk(input_base):
                for file in files:
                    if not self.is_running: break
                    if file.lower().endswith(valid_exts):
                        full_in = os.path.join(root, file)
                        rel = os.path.relpath(full_in, input_base)
                        full_out = os.path.join(output_base, folder_name, os.path.splitext(rel)[0] + ".avif")
                        tasks.append((full_in, full_out, mode, val, max_side))
        
        total = len(tasks)
        if total == 0 or not self.is_running:
            self.reset_ui()
            return

        self.progress["maximum"] = total
        count = 0
        self.lbl_status.config(text=f"変換中... (残り {total} 枚)")
        self.update_idletasks()

        with ProcessPoolExecutor(max_workers=num_threads) as executor:
            try:
                futures = [executor.submit(process_one_image, t) for t in tasks]
                for future in futures:
                    if not self.is_running:
                        break
                    future.result()
                    count += 1
                    self.progress["value"] = count
                    self.lbl_counter.config(text=f"{count} / {total} ({int(count/total*100)}%)")
                    self.lbl_status.config(text=f"変換中... (残り {total - count} 枚)")
                    self.update_idletasks()
            except Exception as e:
                print(f"Error: {e}")

        if self.is_running: 
            self.lbl_status.config(text="完了！")
            messagebox.showinfo("完了", f"{count}枚の処理が完了しました！")
        self.reset_ui()

    def reset_ui(self):
        self.is_running = False
        self.btn_stop.pack_forget()
        self.btn_start.pack(fill=tk.X)
        if not self.lbl_status.cget("text") == "完了！":
            self.lbl_status.config(text="待機中...")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    App().mainloop()