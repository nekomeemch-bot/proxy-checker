"""
プロキシチェックツール
Googleスプレッドシートからプロキシを読み込み、有効性をチェックして結果を書き込む
"""

import gspread
from google.oauth2.service_account import Credentials
import requests
import time
from typing import List, Dict, Tuple
import sys
import json
import os
from datetime import datetime


class ProxyChecker:
    """プロキシチェッカー"""
    
    def __init__(self, credentials_file: str, spreadsheet_key: str, worksheet_name: str = "Sheet1"):
        """
        初期化
        
        Args:
            credentials_file: Googleサービスアカウントの認証情報JSONファイルパス
            spreadsheet_key: スプレッドシートのキー（URLから取得）
            worksheet_name: ワークシート名
        """
        self.credentials_file = credentials_file
        self.spreadsheet_key = spreadsheet_key
        self.worksheet_name = worksheet_name
        self.client = None
        self.worksheet = None
    
    def _get_credentials_path(self):
        """認証情報ファイルのパスを取得（内蔵版対応）"""
        # PyInstallerでビルドされた場合の一時ディレクトリ
        try:
            # PyInstallerでビルドされた場合
            base_path = sys._MEIPASS
            embedded_path = os.path.join(base_path, os.path.basename(self.credentials_file))
            if os.path.exists(embedded_path):
                return embedded_path
        except Exception:
            pass
        
        # 通常のパス
        if os.path.exists(self.credentials_file):
            return self.credentials_file
        
        # ファイル名のみ指定されている場合、カレントディレクトリから探す
        filename = os.path.basename(self.credentials_file)
        if os.path.exists(filename):
            return filename
        
        return self.credentials_file
        
    def connect_spreadsheet(self):
        """スプレッドシートに接続"""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # 内蔵された認証情報ファイルに対応
            credentials_path = self._get_credentials_path()
            creds = Credentials.from_service_account_file(
                credentials_path, scopes=scope
            )
            self.client = gspread.authorize(creds)
            spreadsheet = self.client.open_by_key(self.spreadsheet_key)
            self.worksheet = spreadsheet.worksheet(self.worksheet_name)
            print(f"スプレッドシート '{spreadsheet.title}' に接続しました")
        except FileNotFoundError:
            print(f"エラー: 認証情報ファイル '{self.credentials_file}' が見つかりません")
            print(f"ヒント: config.json の credentials_file のパスを確認してください")
            sys.exit(1)
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"エラー: スプレッドシートが見つかりません")
            print(f"ヒント: スプレッドシートキー '{self.spreadsheet_key}' が正しいか確認してください")
            print(f"       スプレッドシートがサービスアカウントと共有されているか確認してください")
            sys.exit(1)
        except gspread.exceptions.WorksheetNotFound:
            print(f"エラー: ワークシート '{self.worksheet_name}' が見つかりません")
            print(f"ヒント: ワークシート名が正しいか確認してください")
            # 利用可能なワークシートを一覧表示
            try:
                spreadsheet = self.client.open_by_key(self.spreadsheet_key)
                worksheets = spreadsheet.worksheets()
                print(f"\n利用可能なワークシート:")
                for i, ws in enumerate(worksheets, 1):
                    print(f"  {i}. '{ws.title}'")
                print(f"\nconfig.json の worksheet_name を上記のいずれかに変更してください")
            except:
                pass
            sys.exit(1)
        except Exception as e:
            print(f"スプレッドシート接続エラー: {e}")
            print(f"ヒント: 認証情報ファイルとスプレッドシートの設定を確認してください")
            sys.exit(1)
    
    def read_proxies(self, proxy_column: str = "A", start_row: int = 2) -> List[str]:
        """
        スプレッドシートからプロキシを読み込む
        
        Args:
            proxy_column: プロキシが記載されている列（例: "A"）
            start_row: データが開始する行番号（1行目がヘッダーの場合2）
        
        Returns:
            プロキシのリスト
        """
        try:
            # 列の全データを取得
            col_idx = ord(proxy_column.upper()) - ord('A') + 1
            column_data = self.worksheet.col_values(col_idx)
            
            # デバッグ情報
            print(f"列 {proxy_column} の全データ数: {len(column_data)}")
            if len(column_data) > 0:
                print(f"  1行目: {column_data[0] if column_data else '(空)'}")
            if len(column_data) > 1:
                print(f"  2行目: {column_data[1] if len(column_data) > 1 else '(空)'}")
            
            # ヘッダー行を除いて、空でない値を取得
            proxies = [p.strip() for p in column_data[start_row-1:] if p.strip()]
            print(f"{len(proxies)}個のプロキシを読み込みました")
            
            if len(proxies) == 0 and len(column_data) > 0:
                print(f"警告: プロキシが見つかりませんでした。開始行 {start_row} 以降にデータがあるか確認してください。")
                print(f"  列 {proxy_column} のデータ: {column_data[:5]}...")  # 最初の5件を表示
            
            return proxies
        except Exception as e:
            print(f"プロキシ読み込みエラー: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def normalize_proxy(self, proxy: str) -> str:
        """
        プロキシ形式を正規化
        
        Args:
            proxy: プロキシ文字列（複数の形式に対応）
                - "IP:PORT:USERNAME:PASSWORD" → "http://USERNAME:PASSWORD@IP:PORT"
                - "http://user:pass@host:port" → そのまま
                - "host:port" → "http://host:port"
        
        Returns:
            正規化されたプロキシURL
        """
        proxy = proxy.strip()
        
        # 既にhttp://またはhttps://で始まる場合はそのまま
        if proxy.startswith(('http://', 'https://')):
            return proxy
        
        # IP:PORT:USERNAME:PASSWORD 形式をチェック
        parts = proxy.split(':')
        if len(parts) == 4:
            # IP:PORT:USERNAME:PASSWORD 形式
            ip, port, username, password = parts
            return f"http://{username}:{password}@{ip}:{port}"
        elif len(parts) == 2:
            # HOST:PORT 形式
            host, port = parts
            return f"http://{host}:{port}"
        else:
            # その他の形式はそのまま返す（エラーは後で検出される）
            return proxy
    
    def check_proxy(self, proxy: str, timeout: int = 10, test_url: str = "http://httpbin.org/ip", strict: bool = True) -> Tuple[bool, str]:
        """
        プロキシの有効性を厳密にチェック
        
        Args:
            proxy: プロキシアドレス
                - "IP:PORT:USERNAME:PASSWORD" 形式
                - "http://user:pass@host:port" 形式
                - "http://host:port" 形式
            timeout: タイムアウト秒数
            test_url: テスト用URL（デフォルトは使用されず、複数URLでテスト）
            strict: 厳密モード（複数URLでテスト、IP一致確認など）
        
        Returns:
            (有効かどうか, エラーメッセージまたはレスポンス情報)
        """
        import time as time_module
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # プロキシ形式を正規化
        normalized_proxy = self.normalize_proxy(proxy)
        
        # プロキシのIPを抽出（検証用）
        proxy_ip = None
        if ':' in proxy and not proxy.startswith(('http://', 'https://')):
            parts = proxy.split(':')
            if len(parts) >= 1:
                proxy_ip = parts[0]
        
        proxies = {
            'http': normalized_proxy,
            'https': normalized_proxy
        }
        
        # 厳密モード: 複数のテストURLでチェック
        if strict:
            test_urls = [
                "http://httpbin.org/ip",
                "http://api.ipify.org?format=json",
                "http://ip-api.com/json"
            ]
        else:
            test_urls = [test_url]
        
        success_count = 0
        total_tests = len(test_urls)
        results = []
        response_times = []
        
        for test_url_item in test_urls:
            try:
                start_time = time_module.time()
                response = requests.get(
                    test_url_item,
                    proxies=proxies,
                    timeout=timeout,
                    verify=False,
                    allow_redirects=True
                )
                elapsed_time = time_module.time() - start_time
                response_times.append(elapsed_time)
                
                if response.status_code == 200:
                    try:
                        # レスポンスの内容を確認
                        if 'json' in response.headers.get('content-type', '').lower():
                            data = response.json()
                            
                            # 異なるAPIのレスポンス形式に対応
                            origin_ip = None
                            if 'origin' in data:
                                origin_ip = data['origin']
                            elif 'ip' in data:
                                origin_ip = data['ip']
                            elif 'query' in data:
                                origin_ip = data['query']
                            
                            if origin_ip:
                                # originには複数のIPがカンマ区切りで返ってくる場合がある
                                origin_ips = [ip.strip() for ip in str(origin_ip).split(',')]
                                
                                # プロキシのIPと返ってきたoriginのIPが一致するか確認
                                ip_matched = False
                                if proxy_ip:
                                    ip_matched = proxy_ip in origin_ips
                                
                                if ip_matched:
                                    success_count += 1
                                    results.append(f"{test_url_item}: IP一致 ({origin_ip}, {elapsed_time:.2f}秒)")
                                else:
                                    # IPが一致しない場合は警告
                                    if proxy_ip:
                                        results.append(f"{test_url_item}: IP不一致警告 (期待: {proxy_ip}, 実際: {origin_ip}, {elapsed_time:.2f}秒)")
                                    else:
                                        success_count += 1
                                        results.append(f"{test_url_item}: 成功 ({origin_ip}, {elapsed_time:.2f}秒)")
                            else:
                                # IPが取得できない場合
                                results.append(f"{test_url_item}: レスポンス異常 (IP取得失敗, {elapsed_time:.2f}秒)")
                        else:
                            # JSON以外のレスポンス
                            results.append(f"{test_url_item}: 非JSONレスポンス (ステータス200, {elapsed_time:.2f}秒)")
                            success_count += 1
                    except (ValueError, KeyError) as e:
                        results.append(f"{test_url_item}: JSON解析エラー ({str(e)}, {elapsed_time:.2f}秒)")
                else:
                    results.append(f"{test_url_item}: ステータスコード{response.status_code} ({elapsed_time:.2f}秒)")
            except requests.exceptions.ProxyError as e:
                error_msg = str(e)
                if "407" in error_msg or "authentication" in error_msg.lower():
                    results.append(f"{test_url_item}: 認証エラー")
                elif "403" in error_msg or "forbidden" in error_msg.lower():
                    results.append(f"{test_url_item}: アクセス拒否")
                else:
                    results.append(f"{test_url_item}: プロキシエラー ({error_msg[:50]})")
            except requests.exceptions.Timeout:
                results.append(f"{test_url_item}: タイムアウト ({timeout}秒)")
            except requests.exceptions.ConnectionError as e:
                error_msg = str(e)
                if "Name or service not known" in error_msg or "nodename nor servname provided" in error_msg:
                    results.append(f"{test_url_item}: DNS解決エラー")
                elif "Connection refused" in error_msg:
                    results.append(f"{test_url_item}: 接続拒否")
                else:
                    results.append(f"{test_url_item}: 接続エラー ({error_msg[:50]})")
            except requests.exceptions.SSLError as e:
                results.append(f"{test_url_item}: SSLエラー ({str(e)[:50]})")
            except Exception as e:
                results.append(f"{test_url_item}: エラー ({str(e)[:50]})")
        
        # 厳密モード: すべてのテストが成功し、かつIPが一致する場合のみ有効
        if strict:
            avg_time = sum(response_times) / len(response_times) if response_times else 0
            success_rate = success_count / total_tests if total_tests > 0 else 0
            
            # 成功率が80%以上で、かつ平均レスポンス時間が10秒以内の場合に有効と判定
            if success_rate >= 0.8 and avg_time <= 10.0:
                result_msg = f"有効 (成功率: {success_rate*100:.1f}%, 平均: {avg_time:.2f}秒) - " + "; ".join(results)
                return True, result_msg
            else:
                result_msg = f"無効 (成功率: {success_rate*100:.1f}%, 平均: {avg_time:.2f}秒) - " + "; ".join(results)
                return False, result_msg
        else:
            # 非厳密モード: 1つでも成功すれば有効
            if success_count > 0:
                avg_time = sum(response_times) / len(response_times) if response_times else 0
                result_msg = f"成功 ({success_count}/{total_tests}, 平均: {avg_time:.2f}秒) - " + "; ".join(results)
                return True, result_msg
            else:
                result_msg = "失敗 - " + "; ".join(results)
                return False, result_msg
    
    def check_all_proxies(self, proxies: List[str], delay: float = 1.0, strict: bool = True) -> List[Dict]:
        """
        すべてのプロキシをチェック
        
        Args:
            proxies: プロキシのリスト
            delay: チェック間の遅延（秒）
            strict: 厳密モード（複数URLでテスト、IP一致確認など）
        
        Returns:
            チェック結果のリスト [{"proxy": "...", "status": "...", "message": "..."}, ...]
        """
        results = []
        total = len(proxies)
        
        for i, proxy in enumerate(proxies, 1):
            print(f"[{i}/{total}] チェック中: {proxy}")
            is_valid, message = self.check_proxy(proxy, strict=strict)
            
            status = "有効" if is_valid else "無効"
            result = {
                "proxy": proxy,
                "status": status,
                "message": message,
                "is_valid": is_valid
            }
            results.append(result)
            
            print(f"  結果: {status} - {message}")
            
            # 次のチェックまでの遅延
            if i < total:
                time.sleep(delay)
        
        return results
    
    def read_previous_statuses(self, proxy_column: str = "A", status_column: str = "B", start_row: int = 2) -> Dict[str, str]:
        """
        前回のステータスを読み込む
        
        Args:
            proxy_column: プロキシ列
            status_column: ステータス列
            start_row: データ開始行
        
        Returns:
            プロキシをキー、前回のステータスを値とする辞書
        """
        previous_statuses = {}
        try:
            proxies = self.read_proxies(proxy_column, start_row)
            status_col_idx = ord(status_column.upper()) - ord('A') + 1
            
            for i, proxy in enumerate(proxies):
                row = start_row + i
                try:
                    status_value = self.worksheet.cell(row, status_col_idx).value
                    if status_value:
                        previous_statuses[proxy] = status_value.strip()
                except:
                    pass
        except Exception as e:
            print(f"前回ステータス読み込みエラー: {e}")
        
        return previous_statuses
    
    def write_results(self, results: List[Dict], status_column: str = "B", message_column: str = "C", 
                     date_column: str = "D", previous_status_column: str = "E", start_row: int = 2, 
                     track_changes: bool = True):
        """
        チェック結果をスプレッドシートに書き込む
        
        Args:
            results: チェック結果のリスト
            status_column: ステータスを書き込む列（例: "B"）
            message_column: メッセージを書き込む列（例: "C"）
            date_column: チェック日時を書き込む列（例: "D"）
            previous_status_column: 前回ステータスを書き込む列（例: "E"）
            start_row: データが開始する行番号
            track_changes: 変更を追跡するかどうか
        """
        try:
            status_col_idx = ord(status_column.upper()) - ord('A') + 1
            message_col_idx = ord(message_column.upper()) - ord('A') + 1
            date_col_idx = ord(date_column.upper()) - ord('A') + 1
            prev_status_col_idx = ord(previous_status_column.upper()) - ord('A') + 1
            
            # 前回のステータスを読み込む
            previous_statuses = {}
            if track_changes:
                try:
                    # プロキシ列を推測（通常はA列）
                    previous_statuses = self.read_previous_statuses("A", status_column, start_row)
                except:
                    pass
            
            # 現在の日時
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # バッチ更新用のデータを準備
            status_updates = []
            message_updates = []
            date_updates = []
            prev_status_updates = []
            changed_proxies = []
            
            for i, result in enumerate(results):
                row = start_row + i
                proxy = result['proxy']
                current_status = result['status']
                
                status_updates.append({
                    'range': f'{status_column}{row}',
                    'values': [[current_status]]
                })
                message_updates.append({
                    'range': f'{message_column}{row}',
                    'values': [[result['message']]]
                })
                date_updates.append({
                    'range': f'{date_column}{row}',
                    'values': [[current_datetime]]
                })
                
                # 前回のステータスを記録
                if track_changes and proxy in previous_statuses:
                    prev_status = previous_statuses[proxy]
                    prev_status_updates.append({
                        'range': f'{previous_status_column}{row}',
                        'values': [[prev_status]]
                    })
                    
                    # 変更を検出（前回有効→今回無効）
                    if prev_status == "有効" and current_status == "無効":
                        changed_proxies.append(proxy)
                elif track_changes:
                    # 前回のステータスがない場合、現在のステータスを記録
                    prev_status_updates.append({
                        'range': f'{previous_status_column}{row}',
                        'values': [[current_status]]
                    })
            
            # バッチ更新を実行
            if status_updates:
                self.worksheet.batch_update(status_updates)
            if message_updates:
                self.worksheet.batch_update(message_updates)
            if date_updates:
                self.worksheet.batch_update(date_updates)
            if prev_status_updates:
                self.worksheet.batch_update(prev_status_updates)
            
            # ヘッダーを設定（まだ存在しない場合）
            if start_row == 2:
                header_row = self.worksheet.row_values(1)
                max_col_idx = max(status_col_idx, message_col_idx, date_col_idx, prev_status_col_idx)
                if not header_row or len(header_row) < max_col_idx:
                    headers = {}
                    if len(header_row) < status_col_idx:
                        headers[f'{status_column}1'] = 'ステータス'
                    if len(header_row) < message_col_idx:
                        headers[f'{message_column}1'] = 'メッセージ'
                    if len(header_row) < date_col_idx:
                        headers[f'{date_column}1'] = 'チェック日時'
                    if len(header_row) < prev_status_col_idx:
                        headers[f'{previous_status_column}1'] = '前回ステータス'
                    if headers:
                        self.worksheet.batch_update([
                            {'range': k, 'values': [[v]]} for k, v in headers.items()
                        ])
            
            valid_count = sum(1 for r in results if r['is_valid'])
            print(f"\n結果を書き込みました: 有効 {valid_count}/{len(results)}")
            
            # 無効になったプロキシを報告
            if changed_proxies:
                print(f"\n⚠️  無効になったプロキシ ({len(changed_proxies)}個):")
                for proxy in changed_proxies[:10]:  # 最初の10個のみ表示
                    print(f"  - {proxy}")
                if len(changed_proxies) > 10:
                    print(f"  ... 他 {len(changed_proxies) - 10}個")
                return changed_proxies
            
            return []
        except Exception as e:
            print(f"結果書き込みエラー: {e}")
            sys.exit(1)
    
    def run(self, proxy_column: str = "A", status_column: str = "B", message_column: str = "C", 
            date_column: str = "D", previous_status_column: str = "E", start_row: int = 2, 
            delay: float = 1.0, strict: bool = True, track_changes: bool = True):
        """
        メイン処理を実行
        
        Args:
            proxy_column: プロキシ列
            status_column: ステータス列
            message_column: メッセージ列
            date_column: チェック日時列
            previous_status_column: 前回ステータス列
            start_row: 開始行
            delay: チェック間の遅延
            strict: 厳密モード（複数URLでテスト、IP一致確認など）
            track_changes: 変更を追跡するかどうか
        """
        print("=== プロキシチェックツール ===\n")
        if strict:
            print("厳密モード: 有効（複数URLでテスト、IP一致確認）\n")
        else:
            print("通常モード: 有効\n")
        
        # スプレッドシートに接続
        self.connect_spreadsheet()
        
        # プロキシを読み込む
        proxies = self.read_proxies(proxy_column, start_row)
        
        if not proxies:
            print("プロキシが見つかりませんでした")
            return []
        
        # プロキシをチェック
        print(f"\nプロキシチェックを開始します...\n")
        results = self.check_all_proxies(proxies, delay, strict)
        
        # 結果を書き込む
        print(f"\n結果をスプレッドシートに書き込んでいます...")
        changed_proxies = self.write_results(
            results, status_column, message_column, date_column, 
            previous_status_column, start_row, track_changes
        )
        
        # サマリーを表示
        valid_count = sum(1 for r in results if r['is_valid'])
        invalid_count = len(results) - valid_count
        print(f"\n=== チェック完了 ===")
        print(f"有効: {valid_count}")
        print(f"無効: {invalid_count}")
        print(f"合計: {len(results)}")
        
        return changed_proxies


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='プロキシチェックツール')
    parser.add_argument('--config', '-f',
                       help='設定ファイルのパス（JSON形式）')
    parser.add_argument('--credentials', '-c',
                       help='Googleサービスアカウントの認証情報JSONファイルパス')
    parser.add_argument('--spreadsheet-key', '-k',
                       help='スプレッドシートのキー（URLの/d/と/edit/の間の文字列）')
    parser.add_argument('--worksheet', '-w',
                       help='ワークシート名（デフォルト: Sheet1）')
    parser.add_argument('--proxy-column', '-pc',
                       help='プロキシ列（デフォルト: A）')
    parser.add_argument('--status-column', '-sc',
                       help='ステータス列（デフォルト: B）')
    parser.add_argument('--message-column', '-mc',
                       help='メッセージ列（デフォルト: C）')
    parser.add_argument('--start-row', '-sr', type=int,
                       help='データ開始行（デフォルト: 2）')
    parser.add_argument('--delay', '-d', type=float,
                       help='チェック間の遅延秒数（デフォルト: 1.0）')
    parser.add_argument('--strict', action='store_true', default=True,
                       help='厳密モード（複数URLでテスト、IP一致確認）')
    parser.add_argument('--no-strict', dest='strict', action='store_false',
                       help='通常モード（1つのURLのみでテスト）')
    parser.add_argument('--date-column', '-dc', default='D',
                       help='チェック日時列（デフォルト: D）')
    parser.add_argument('--previous-status-column', '-psc', default='E',
                       help='前回ステータス列（デフォルト: E）')
    parser.add_argument('--no-track-changes', dest='track_changes', action='store_false', default=True,
                       help='変更追跡を無効化')
    
    args = parser.parse_args()
    
    # 設定ファイルから読み込む
    config = {}
    if args.config:
        if not os.path.exists(args.config):
            print(f"エラー: 設定ファイル '{args.config}' が見つかりません")
            print(f"ヒント: config.example.json を config.json にコピーして設定してください")
            sys.exit(1)
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            print(f"エラー: 設定ファイル '{args.config}' のJSON形式が正しくありません: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"エラー: 設定ファイルの読み込みエラー: {e}")
            sys.exit(1)
    
    # コマンドライン引数が優先される（指定されていない場合は設定ファイルから読み込む）
    credentials_file = args.credentials or config.get('credentials_file')
    spreadsheet_key = args.spreadsheet_key or config.get('spreadsheet_key')
    worksheet_name = args.worksheet or config.get('worksheet_name', 'Sheet1')
    proxy_column = args.proxy_column or config.get('proxy_column', 'A')
    status_column = args.status_column or config.get('status_column', 'B')
    message_column = args.message_column or config.get('message_column', 'C')
    start_row = args.start_row if args.start_row is not None else config.get('start_row', 2)
    delay = args.delay if args.delay is not None else config.get('delay', 1.0)
    
    # 必須パラメータのチェック
    if not credentials_file:
        print("エラー: --credentials または設定ファイルで credentials_file を指定してください")
        sys.exit(1)
    
    # 認証情報ファイルの存在確認
    if not os.path.exists(credentials_file):
        print(f"エラー: 認証情報ファイル '{credentials_file}' が見つかりません")
        print(f"ヒント: Google Cloud Console でサービスアカウントを作成し、JSONキーをダウンロードしてください")
        print(f"       README.md の「セットアップ」セクションを参照してください")
        sys.exit(1)
    
    if not spreadsheet_key:
        print("エラー: --spreadsheet-key または設定ファイルで spreadsheet_key を指定してください")
        sys.exit(1)
    
    # スプレッドシートキーがデフォルト値でないか確認
    if spreadsheet_key == "your-spreadsheet-key-here":
        print("エラー: スプレッドシートキーが設定されていません")
        print("ヒント: config.json の spreadsheet_key を実際のスプレッドシートキーに変更してください")
        print("       スプレッドシートのURL: https://docs.google.com/spreadsheets/d/SPREADSHEET_KEY/edit")
        sys.exit(1)
    
    checker = ProxyChecker(
        credentials_file=credentials_file,
        spreadsheet_key=spreadsheet_key,
        worksheet_name=worksheet_name
    )
    
    strict_mode = args.strict if args.strict is not None else config.get('strict', True)
    date_column = args.date_column or config.get('date_column', 'D')
    previous_status_column = args.previous_status_column or config.get('previous_status_column', 'E')
    track_changes = args.track_changes if hasattr(args, 'track_changes') else config.get('track_changes', True)
    
    changed_proxies = checker.run(
        proxy_column=proxy_column,
        status_column=status_column,
        message_column=message_column,
        date_column=date_column,
        previous_status_column=previous_status_column,
        start_row=start_row,
        delay=delay,
        strict=strict_mode,
        track_changes=track_changes
    )
    
    # 無効になったプロキシがある場合、終了コード1で終了（スケジュール実行時の通知用）
    if changed_proxies:
        sys.exit(1)


if __name__ == '__main__':
    main()
