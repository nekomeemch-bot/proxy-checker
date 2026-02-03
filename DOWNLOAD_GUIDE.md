# ダウンロード方法

## Gitを使用する方法（推奨）

### 1. Gitをインストール

まだインストールしていない場合:
- Windows: https://git-scm.com/download/win からダウンロード
- macOS: `brew install git` または Xcode Command Line Tools
- Linux: `sudo apt install git` (Ubuntu/Debian) または `sudo yum install git` (CentOS/RHEL)

### 2. リポジトリをクローン

```bash
git clone https://github.com/nekomeemch-bot/proxy-checker.git
```

### 3. ディレクトリに移動

```bash
cd proxy-checker
```

### 4. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

## ZIPファイルでダウンロードする方法

### 1. GitHubのリポジトリページにアクセス

https://github.com/nekomeemch-bot/proxy-checker

### 2. ZIPファイルをダウンロード

1. ページ右上の緑色の「Code」ボタンをクリック
2. 「Download ZIP」を選択
3. ZIPファイルをダウンロード

### 3. ZIPファイルを展開

ダウンロードしたZIPファイルを展開します。

### 4. 依存パッケージをインストール

展開したフォルダで:

```bash
cd proxy-checker
pip install -r requirements.txt
```

## セットアップ

### 1. 認証情報ファイルの準備

1. Google Cloud Consoleでサービスアカウントを作成
2. JSONキーをダウンロード
3. プロジェクトフォルダに `credentials.json` として保存

### 2. 設定ファイルの作成

```bash
# 設定ファイルのテンプレートをコピー
copy config.example.json config.json
```

または:

```bash
# Linux/macOSの場合
cp config.example.json config.json
```

### 3. 設定ファイルを編集

`config.json` を開いて以下を設定:

```json
{
  "credentials_file": "credentials.json",
  "spreadsheet_key": "YOUR_SPREADSHEET_KEY",
  "worksheet_name": "シート1",
  "proxy_column": "A",
  "status_column": "B",
  "message_column": "C",
  "start_row": 2,
  "delay": 1.0
}
```

## 使用方法

### GUI版（推奨）

```bash
python proxy_checker_gui.py
```

### コマンドライン版

```bash
python proxy_checker.py --config config.json
```

## 更新方法

### Gitを使用している場合

```bash
git pull
```

### ZIPファイルでダウンロードした場合

再度ZIPファイルをダウンロードして上書きするか、Gitを使用する方法に切り替えてください。
