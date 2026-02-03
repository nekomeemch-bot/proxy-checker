# GitHub Releases作成ガイド

## 方法1: コマンドラインから作成（簡単・推奨）

### Windows (PowerShell)

```powershell
# GitHub CLIがインストールされている場合
.\create_release.ps1

# バージョンを指定する場合
.\create_release.ps1 -Version "v1.0.1"
```

### Linux/macOS

```bash
chmod +x create_release.sh
./create_release.sh

# バージョンを指定する場合
./create_release.sh v1.0.1
```

### GitHub CLIのインストール

**Windows:**
```powershell
winget install --id GitHub.cli
```

**macOS:**
```bash
brew install gh
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install gh

# または公式サイトから: https://cli.github.com/
```

### 初回使用時

```bash
gh auth login
```

## 方法2: Webブラウザから作成

### 1. GitHubリポジトリページにアクセス

https://github.com/nekomeemch-bot/proxy-checker

### 2. Releasesセクションに移動

1. リポジトリページの右側にある「Releases」をクリック
   - または、URLに直接 `/releases` を追加: https://github.com/nekomeemch-bot/proxy-checker/releases

### 3. 新しいリリースを作成

1. 「Create a new release」ボタンをクリック
2. または、「Draft a new release」をクリック

### 4. リリース情報を入力

#### タグの作成
- **Choose a tag**: 新しいタグを作成（例: `v1.0.0`）
- **Target**: `main` ブランチを選択

#### リリースタイトル
- 例: `v1.0.0 - 初回リリース`
- または: `プロキシチェックツール v1.0.0`

#### 説明（リリースノート）
以下のテンプレートを使用できます:

```markdown
## プロキシチェックツール v1.0.0

### 機能
- Googleスプレッドシートからプロキシを読み込み
- 各プロキシの有効性を自動チェック（厳密モード対応）
- チェック結果をスプレッドシートに書き込み
- チェック日時の記録
- 変更追跡（無効になったプロキシを自動検出）
- 定期的な自動チェック機能
- GUI版とコマンドライン版の両方をサポート

### ダウンロード
- **proxy_checker.exe**: GUI版アプリケーション（認証情報ファイル内蔵版）

### 使用方法
1. `proxy_checker.exe` をダウンロード
2. 実行してGUIを起動
3. スプレッドシートキーを入力
4. 「チェック開始」をクリック

### 注意事項
- 認証情報ファイルが内蔵されているため、exeファイルを解析すると認証情報が漏洩する可能性があります
- セキュリティを重視する場合は、ソースコードからビルドして使用してください
```

### 5. ファイルをアップロード

1. 「Attach binaries by dropping them here or selecting them」セクションに
2. `dist/proxy_checker.exe` をドラッグ&ドロップ
   - または、「selecting them」をクリックしてファイルを選択

### 6. リリースを公開

1. 「Publish release」ボタンをクリック
   - 下書きとして保存する場合は「Save draft」をクリック

## リリース後の確認

リリースが作成されると:
- リポジトリの「Releases」セクションに表示されます
- ダウンロードリンクが利用可能になります
- リリースノートが表示されます

## リリースの更新

既存のリリースを更新する場合:
1. リリースページで「Edit release」をクリック
2. 新しいファイルを追加または更新
3. 「Update release」をクリック
