"""
認証情報ファイルを内蔵したバージョン
exe化する際に使用
"""

import sys
import os
import json
from pathlib import Path

# PyInstallerでビルドされた場合の一時ディレクトリ
def get_resource_path(relative_path):
    """リソースファイルのパスを取得（PyInstaller対応）"""
    try:
        # PyInstallerでビルドされた場合
        base_path = sys._MEIPASS
    except Exception:
        # 通常の実行時
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def load_embedded_credentials():
    """内蔵された認証情報ファイルを読み込む"""
    credentials_path = get_resource_path("credentials.json")
    
    if os.path.exists(credentials_path):
        try:
            with open(credentials_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"認証情報ファイルの読み込みエラー: {e}")
            return None
    else:
        # 内蔵されていない場合、通常のパスから読み込む
        if os.path.exists("credentials.json"):
            try:
                with open("credentials.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"認証情報ファイルの読み込みエラー: {e}")
                return None
    return None

def get_credentials_file_path():
    """認証情報ファイルのパスを取得（内蔵版対応）"""
    # まず内蔵されたファイルを確認
    embedded_path = get_resource_path("credentials.json")
    if os.path.exists(embedded_path):
        return embedded_path
    
    # 次に通常のパスを確認
    if os.path.exists("credentials.json"):
        return "credentials.json"
    
    return None
