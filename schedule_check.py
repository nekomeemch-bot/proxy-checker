"""
定期的な自動チェック用スクリプト
Windowsタスクスケジューラから実行することを想定
"""

import sys
import os
from proxy_checker import ProxyChecker, main

if __name__ == '__main__':
    # 設定ファイルから読み込む
    config_file = "config.json"
    if not os.path.exists(config_file):
        print(f"エラー: 設定ファイル '{config_file}' が見つかりません")
        sys.exit(1)
    
    # メイン処理を実行
    try:
        main()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)
