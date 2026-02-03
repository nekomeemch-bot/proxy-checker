# GitHub Releases作成スクリプト
# GitHub CLIを使用してリリースを作成

param(
    [string]$Version = "v1.0.0",
    [string]$Title = "",
    [string]$Notes = ""
)

# デフォルトのタイトル
if ([string]::IsNullOrEmpty($Title)) {
    $Title = "$Version - プロキシチェックツール"
}

# デフォルトのリリースノート
if ([string]::IsNullOrEmpty($Notes)) {
    $Notes = @"
## プロキシチェックツール $Version

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
"@
}

# exeファイルのパス
$exePath = "dist\proxy_checker.exe"

# exeファイルが存在するか確認
if (-not (Test-Path $exePath)) {
    Write-Host "エラー: $exePath が見つかりません" -ForegroundColor Red
    Write-Host "まず build_exe.py を実行してexeファイルを作成してください" -ForegroundColor Yellow
    exit 1
}

Write-Host "GitHub Releasesを作成しています..." -ForegroundColor Green
Write-Host "バージョン: $Version" -ForegroundColor Cyan
Write-Host "タイトル: $Title" -ForegroundColor Cyan

# GitHub CLIでリリースを作成
try {
    gh release create $Version `
        --title "$Title" `
        --notes "$Notes" `
        "$exePath"
    
    Write-Host "`n✓ リリースが作成されました！" -ForegroundColor Green
    Write-Host "https://github.com/nekomeemch-bot/proxy-checker/releases" -ForegroundColor Cyan
} catch {
    Write-Host "`nエラー: リリースの作成に失敗しました" -ForegroundColor Red
    Write-Host "GitHub CLIがインストールされていない場合:" -ForegroundColor Yellow
    Write-Host "  winget install --id GitHub.cli" -ForegroundColor Yellow
    Write-Host "または: https://cli.github.com/ からインストールしてください" -ForegroundColor Yellow
    exit 1
}
