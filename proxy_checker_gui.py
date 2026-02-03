"""
プロキシチェックツール - GUI版
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
from proxy_checker import ProxyChecker


class ProxyCheckerGUI:
    """プロキシチェッカーGUIアプリケーション"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("プロキシチェックツール")
        self.root.geometry("800x700")
        
        # 変数
        self.credentials_file = tk.StringVar()
        self.spreadsheet_key = tk.StringVar()
        self.worksheet_name = tk.StringVar(value="シート1")
        self.proxy_column = tk.StringVar(value="A")
        self.status_column = tk.StringVar(value="B")
        self.message_column = tk.StringVar(value="C")
        self.date_column = tk.StringVar(value="D")
        self.previous_status_column = tk.StringVar(value="E")
        self.start_row = tk.IntVar(value=2)
        self.delay = tk.DoubleVar(value=1.0)
        self.strict_mode = tk.BooleanVar(value=True)
        self.track_changes = tk.BooleanVar(value=True)
        
        self.is_running = False
        self.checker = None
        
        self.create_widgets()
        
        # 設定ファイルから読み込みを試行
        self.load_config()
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 設定セクション
        settings_frame = ttk.LabelFrame(main_frame, text="設定", padding="10")
        settings_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 認証情報ファイル
        ttk.Label(settings_frame, text="認証情報ファイル:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.credentials_file, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(settings_frame, text="参照", command=self.browse_credentials).grid(row=0, column=2, padx=5, pady=5)
        
        # スプレッドシートキー
        ttk.Label(settings_frame, text="スプレッドシートキー:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.spreadsheet_key, width=50).grid(row=1, column=1, padx=5, pady=5)
        
        # ワークシート名
        ttk.Label(settings_frame, text="ワークシート名:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.worksheet_name, width=50).grid(row=2, column=1, padx=5, pady=5)
        
        # 列設定
        columns_frame = ttk.Frame(settings_frame)
        columns_frame.grid(row=3, column=0, columnspan=3, pady=5)
        
        ttk.Label(columns_frame, text="プロキシ列:").grid(row=0, column=0, padx=5)
        ttk.Entry(columns_frame, textvariable=self.proxy_column, width=5).grid(row=0, column=1, padx=5)
        
        ttk.Label(columns_frame, text="ステータス列:").grid(row=0, column=2, padx=5)
        ttk.Entry(columns_frame, textvariable=self.status_column, width=5).grid(row=0, column=3, padx=5)
        
        ttk.Label(columns_frame, text="メッセージ列:").grid(row=0, column=4, padx=5)
        ttk.Entry(columns_frame, textvariable=self.message_column, width=5).grid(row=0, column=5, padx=5)
        
        # その他の設定
        ttk.Label(settings_frame, text="開始行:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(settings_frame, from_=1, to=1000, textvariable=self.start_row, width=10).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="チェック間隔(秒):").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(settings_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.delay, width=10).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 厳密モード
        ttk.Checkbutton(settings_frame, text="厳密モード（複数URLでテスト、IP一致確認）", variable=self.strict_mode).grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 変更追跡
        ttk.Checkbutton(settings_frame, text="変更追跡（無効になったプロキシを検出）", variable=self.track_changes).grid(row=7, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 列設定（詳細）
        columns_detail_frame = ttk.LabelFrame(settings_frame, text="列設定（詳細）", padding="5")
        columns_detail_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(columns_detail_frame, text="チェック日時列:").grid(row=0, column=0, padx=5)
        ttk.Entry(columns_detail_frame, textvariable=self.date_column, width=5).grid(row=0, column=1, padx=5)
        
        ttk.Label(columns_detail_frame, text="前回ステータス列:").grid(row=0, column=2, padx=5)
        ttk.Entry(columns_detail_frame, textvariable=self.previous_status_column, width=5).grid(row=0, column=3, padx=5)
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="チェック開始", command=self.start_check, width=20)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="設定を保存", command=self.save_config, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="設定を読み込み", command=self.load_config, width=20).pack(side=tk.LEFT, padx=5)
        
        # 進捗バー
        self.progress_var = tk.StringVar(value="待機中...")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=2, column=0, columnspan=2, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # ログ表示
        log_frame = ttk.LabelFrame(main_frame, text="ログ", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # グリッドの重み設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        settings_frame.columnconfigure(1, weight=1)
    
    def browse_credentials(self):
        """認証情報ファイルを選択"""
        filename = filedialog.askopenfilename(
            title="認証情報ファイルを選択",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.credentials_file.set(filename)
    
    def log(self, message):
        """ログにメッセージを追加"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_check(self):
        """チェックを開始"""
        if self.is_running:
            messagebox.showwarning("警告", "既にチェックが実行中です")
            return
        
        # バリデーション
        if not self.credentials_file.get():
            messagebox.showerror("エラー", "認証情報ファイルを指定してください")
            return
        
        if not os.path.exists(self.credentials_file.get()):
            messagebox.showerror("エラー", f"認証情報ファイルが見つかりません: {self.credentials_file.get()}")
            return
        
        if not self.spreadsheet_key.get():
            messagebox.showerror("エラー", "スプレッドシートキーを入力してください")
            return
        
        # 別スレッドで実行
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.progress_bar.start()
        self.log_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self.run_check, daemon=True)
        thread.start()
    
    def run_check(self):
        """チェックを実行（別スレッド）"""
        try:
            self.log("=== プロキシチェックツール ===\n")
            
            # ProxyCheckerのインスタンスを作成
            self.checker = ProxyChecker(
                credentials_file=self.credentials_file.get(),
                spreadsheet_key=self.spreadsheet_key.get(),
                worksheet_name=self.worksheet_name.get()
            )
            
            # スプレッドシートに接続
            self.log("スプレッドシートに接続中...")
            self.progress_var.set("スプレッドシートに接続中...")
            self.checker.connect_spreadsheet()
            self.log(f"スプレッドシート '{self.checker.worksheet.spreadsheet.title}' に接続しました\n")
            
            # プロキシを読み込む
            self.log("プロキシを読み込み中...")
            self.progress_var.set("プロキシを読み込み中...")
            proxies = self.checker.read_proxies(
                proxy_column=self.proxy_column.get(),
                start_row=self.start_row.get()
            )
            
            if not proxies:
                self.log("プロキシが見つかりませんでした")
                self.finish_check()
                return
            
            self.log(f"{len(proxies)}個のプロキシを読み込みました\n")
            
            # プロキシをチェック
            self.log("プロキシチェックを開始します...\n")
            self.progress_var.set(f"プロキシをチェック中... (0/{len(proxies)})")
            
            # カスタムチェック関数（進捗表示付き）
            results = []
            total = len(proxies)
            
            for i, proxy in enumerate(proxies, 1):
                if not self.is_running:  # キャンセルチェック
                    break
                
                self.progress_var.set(f"プロキシをチェック中... ({i}/{total})")
                self.log(f"[{i}/{total}] チェック中: {proxy}")
                
                is_valid, message = self.checker.check_proxy(proxy, strict=self.strict_mode.get())
                status = "有効" if is_valid else "無効"
                
                result = {
                    "proxy": proxy,
                    "status": status,
                    "message": message,
                    "is_valid": is_valid
                }
                results.append(result)
                
                self.log(f"  結果: {status} - {message}")
                
                if i < total:
                    import time
                    time.sleep(self.delay.get())
            
            # 結果を書き込む
            if self.is_running and results:
                self.log(f"\n結果をスプレッドシートに書き込んでいます...")
                self.progress_var.set("結果を書き込み中...")
                changed_proxies = self.checker.write_results(
                    results,
                    status_column=self.status_column.get(),
                    message_column=self.message_column.get(),
                    date_column=self.date_column.get(),
                    previous_status_column=self.previous_status_column.get(),
                    start_row=self.start_row.get(),
                    track_changes=self.track_changes.get()
                )
                
                valid_count = sum(1 for r in results if r['is_valid'])
                invalid_count = len(results) - valid_count
                
                self.log(f"\n=== チェック完了 ===")
                self.log(f"有効: {valid_count}")
                self.log(f"無効: {invalid_count}")
                self.log(f"合計: {len(results)}")
                
                # 無効になったプロキシを報告
                if changed_proxies:
                    self.log(f"\n⚠️  無効になったプロキシ ({len(changed_proxies)}個):")
                    for proxy in changed_proxies[:10]:  # 最初の10個のみ表示
                        self.log(f"  - {proxy}")
                    if len(changed_proxies) > 10:
                        self.log(f"  ... 他 {len(changed_proxies) - 10}個")
                    
                    messagebox.showwarning(
                        "チェック完了（警告）", 
                        f"チェックが完了しました\n\n有効: {valid_count}\n無効: {invalid_count}\n合計: {len(results)}\n\n⚠️ 無効になったプロキシ: {len(changed_proxies)}個"
                    )
                else:
                    messagebox.showinfo("完了", f"チェックが完了しました\n有効: {valid_count}\n無効: {invalid_count}")
            
        except Exception as e:
            self.log(f"\nエラーが発生しました: {e}")
            messagebox.showerror("エラー", f"エラーが発生しました:\n{e}")
        finally:
            self.finish_check()
    
    def finish_check(self):
        """チェック終了処理"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.progress_bar.stop()
        self.progress_var.set("待機中...")
    
    def save_config(self):
        """設定をconfig.jsonに保存"""
        try:
            config = {
                "credentials_file": self.credentials_file.get(),
                "spreadsheet_key": self.spreadsheet_key.get(),
                "worksheet_name": self.worksheet_name.get(),
                "proxy_column": self.proxy_column.get(),
                "status_column": self.status_column.get(),
                "message_column": self.message_column.get(),
                "date_column": self.date_column.get(),
                "previous_status_column": self.previous_status_column.get(),
                "start_row": self.start_row.get(),
                "delay": self.delay.get(),
                "strict": self.strict_mode.get(),
                "track_changes": self.track_changes.get()
            }
            
            filename = filedialog.asksaveasfilename(
                title="設定を保存",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                import json
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"設定を保存しました: {filename}")
        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存に失敗しました:\n{e}")
    
    def load_config(self):
        """config.jsonから設定を読み込み"""
        config_file = "config.json"
        if os.path.exists(config_file):
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.credentials_file.set(config.get('credentials_file', ''))
                self.spreadsheet_key.set(config.get('spreadsheet_key', ''))
                self.worksheet_name.set(config.get('worksheet_name', 'シート1'))
                self.proxy_column.set(config.get('proxy_column', 'A'))
                self.status_column.set(config.get('status_column', 'B'))
                self.message_column.set(config.get('message_column', 'C'))
                self.start_row.set(config.get('start_row', 2))
                self.delay.set(config.get('delay', 1.0))
                
                self.log(f"設定を読み込みました: {config_file}")
            except Exception as e:
                self.log(f"設定の読み込みに失敗しました: {e}")


def main():
    """メイン関数"""
    root = tk.Tk()
    app = ProxyCheckerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
