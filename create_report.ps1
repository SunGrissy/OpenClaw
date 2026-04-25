$contents = Get-Content "D:\OpenClaw\workspace\daily_report.json" -Raw
dws report create --template-id "153363afc40e225078a5a254ded82265" --contents $contents --dry-run
