@echo off
REM 定期的な自動チェック用バッチファイル
REM Windowsタスクスケジューラから実行することを想定

cd /d "%~dp0"
python schedule_check.py >> schedule_log.txt 2>&1

REM エラーが発生した場合（無効になったプロキシがある場合）はログに記録
if errorlevel 1 (
    echo [%date% %time%] チェック完了: 無効になったプロキシが検出されました >> schedule_error_log.txt
)
