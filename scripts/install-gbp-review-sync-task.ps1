#Requires -Version 5.1
# Daily GBP review-count sync for knightgroup.com.
# Run elevated if Register-ScheduledTask is denied, then:
#   .\scripts\install-gbp-review-sync-task.ps1
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
$TaskName = "KnightGroupGbpReviewSync"
$Runner = Join-Path $PSScriptRoot "run-gbp-review-sync_hidden.vbs"
if (-not (Test-Path $Runner)) { throw "Missing $Runner" }

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction `
  -Execute "wscript.exe" `
  -Argument "//B //Nologo `"$Runner`"" `
  -WorkingDirectory $PSScriptRoot
# 8:15 AM local — after Property Radar 7:30, before review-ask hours.
$trigger = New-ScheduledTaskTrigger -Daily -At "8:15AM"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Host "Registered $TaskName -> $Runner (daily 8:15 AM)" -ForegroundColor Green
Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, State
