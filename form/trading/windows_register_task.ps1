param(
  [string]$Owner = "Sister",
  [switch]$LogonRepl
)

$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if (-not (Test-Path (Join-Path $Root "form"))) {
  $Root = (Get-Location).Path
}

$Python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Python) { $Python = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $Python) { Write-Error "Python not found on PATH"; exit 1 }

$DailyName = "DellMatrix_Daily_$Owner"
$DailyArgs = "-m form.trading.cli --owner $Owner daily"

# Remove old if present
schtasks /Delete /TN $DailyName /F 2>$null | Out-Null

$Action = New-ScheduledTaskAction -Execute $Python -Argument $DailyArgs -WorkingDirectory $Root
$Trigger = New-ScheduledTaskTrigger -Daily -At 9:35AM
Register-ScheduledTask -TaskName $DailyName -Action $Action -Trigger $Trigger -Description "Dell Matrix trading daily evolve for $Owner" -Force | Out-Null
Write-Host "Registered daily task: $DailyName at 9:35 AM"
Write-Host "Root: $Root"

if ($LogonRepl) {
  $ReplName = "DellMatrix_Repl_$Owner"
  schtasks /Delete /TN $ReplName /F 2>$null | Out-Null
  $ReplArgs = "-m form.repl --owner $Owner --load"
  $RAction = New-ScheduledTaskAction -Execute $Python -Argument $ReplArgs -WorkingDirectory $Root
  $RTrigger = New-ScheduledTaskTrigger -AtLogOn
  Register-ScheduledTask -TaskName $ReplName -Action $RAction -Trigger $RTrigger -Description "Dell Matrix REPL on logon for $Owner" -Force | Out-Null
  Write-Host "Registered logon REPL: $ReplName"
}

Write-Host "Done. Test: python -m form.trading.cli --owner $Owner daily"
