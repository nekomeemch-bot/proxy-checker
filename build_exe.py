"""
exe化用のビルドスクリプト
PyInstallerを使用してexeファイルを作成
"""

import PyInstaller.__main__
import os
import sys

# ビルド設定
app_name = "proxy_checker"
script = "proxy_checker_gui.py"
icon = None  # アイコンファイルがある場合は指定

# 追加ファイル（認証情報ファイルなど）
add_data = []

# 認証情報ファイルが存在する場合、内蔵する
credentials_file = "credentials.json"
if os.path.exists(credentials_file):
    add_data.append(f"{credentials_file};.")

# 設定ファイルも内蔵する場合
config_file = "config.json"
if os.path.exists(config_file):
    add_data.append(f"{config_file};.")

# PyInstallerのオプション
options = [
    script,
    '--name', app_name,
    '--onefile',  # 単一のexeファイルに
    '--windowed',  # コンソールウィンドウを表示しない（GUI用）
    '--clean',  # ビルドキャッシュをクリア
]

# 追加ファイルがある場合
for data in add_data:
    options.extend(['--add-data', data])

# アイコンがある場合
if icon and os.path.exists(icon):
    options.extend(['--icon', icon])

# ビルド実行
print("exeファイルをビルドしています...")
PyInstaller.__main__.run(options)
print(f"\n完了！ dist/{app_name}.exe が作成されました。")
