#!/bin/bash
# GitHub Releases作成スクリプト（Linux/macOS用）
# GitHub CLIを使用してリリースを作成

VERSION=${1:-"v1.0.0"}
TITLE=${2:-"$VERSION - プロキシチェックツール"}

# exeファイルのパス（Linux/macOSでは使用しないが、参考として）
EXE_PATH="dist/proxy_checker.exe"

# リリースノート
NOTES="## プロキシチェックツール $VERSION

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
1. \`proxy_checker.exe\` をダウンロード
2. 実行してGUIを起動
3. スプレッドシートキーを入力
4. 「チェック開始」をクリック"

echo "GitHub Releasesを作成しています..."
echo "バージョン: $VERSION"
echo "タイトル: $TITLE"

# GitHub CLIでリリースを作成
if [ -f "$EXE_PATH" ]; then
    gh release create "$VERSION" \
        --title "$TITLE" \
        --notes "$NOTES" \
        "$EXE_PATH"
else
    echo "警告: $EXE_PATH が見つかりません"
    gh release create "$VERSION" \
        --title "$TITLE" \
        --notes "$NOTES"
fi

echo ""
echo "✓ リリースが作成されました！"
echo "https://github.com/nekomeemch-bot/proxy-checker/releases"
