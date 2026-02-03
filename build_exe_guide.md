# exe化ガイド

## 概要

このガイドでは、プロキシチェックツールをexeファイルに変換する方法を説明します。

## セキュリティ上の注意

⚠️ **重要**: 認証情報ファイル（credentials.json）をexeに内蔵すると、exeファイルを解析することで認証情報が漏洩する可能性があります。

- **推奨**: 認証情報ファイルは別途配布し、exeと同じフォルダに配置する方法
- **非推奨**: 認証情報ファイルをexeに内蔵する方法（セキュリティリスクあり）

## 方法1: 認証情報ファイルを別途配布（推奨）

### 手順

1. **PyInstallerをインストール**
   ```bash
   pip install pyinstaller
   ```

2. **exeファイルをビルド**
   ```bash
   pyinstaller --name proxy_checker --onefile --windowed proxy_checker_gui.py
   ```

3. **配布ファイル**
   - `dist/proxy_checker.exe`
   - `credentials.json`（別途配布）
   - `config.json`（オプション、設定済みの場合）

4. **使用方法**
   - exeファイルとcredentials.jsonを同じフォルダに配置
   - exeファイルを実行

## 方法2: 認証情報ファイルを内蔵（非推奨）

### 手順

1. **認証情報ファイルを準備**
   - `credentials.json` をプロジェクトフォルダに配置

2. **ビルドスクリプトを実行**
   ```bash
   python build_exe.py
   ```

   または手動で:
   ```bash
   pyinstaller --name proxy_checker --onefile --windowed --add-data "credentials.json;." proxy_checker_gui.py
   ```

3. **配布ファイル**
   - `dist/proxy_checker.exe`（認証情報が内蔵されている）

4. **使用方法**
   - exeファイルを実行するだけ（認証情報ファイル不要）

### セキュリティリスク

- exeファイルを解析することで認証情報が漏洩する可能性
- exeファイルを共有する際は注意が必要
- 本番環境では推奨されません

## 方法3: 環境変数から読み込む（中程度のセキュリティ）

認証情報を環境変数から読み込む方法も実装可能です。必要であれば追加します。

## ビルドオプションの説明

- `--onefile`: 単一のexeファイルにまとめる
- `--windowed`: コンソールウィンドウを表示しない（GUI用）
- `--add-data`: 追加ファイルを内蔵する
- `--icon`: アイコンファイルを指定（オプション）

## トラブルシューティング

### エラー: "ModuleNotFoundError"

必要なモジュールが不足している場合:
```bash
pip install -r requirements.txt
```

### exeファイルが大きい

不要なモジュールを除外:
```bash
pyinstaller --exclude-module matplotlib --exclude-module numpy ...
```

### 実行時にエラーが発生する

デバッグモードで実行:
```bash
pyinstaller --debug=all proxy_checker_gui.py
```
