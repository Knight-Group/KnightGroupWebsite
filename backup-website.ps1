# Website Backup Script
# Creates incremental backups of the Knight Group website with version tracking
# Usage: Run this script from the website root directory

param(
    [string]$BackupPath = "C:\Users\nknig\Downloads\WebsiteBackups",
    [switch]$Major = $false
)

# Get the current directory (should be the website root)
$SourcePath = Get-Location
$ProjectName = "KnightGroupWebsite"

# Create backup directory if it doesn't exist
if (-not (Test-Path $BackupPath)) {
    New-Item -ItemType Directory -Path $BackupPath -Force
    Write-Host "Created backup directory: $BackupPath" -ForegroundColor Green
}

# Function to get the next version number
function Get-NextVersion {
    param([string]$BackupDir, [bool]$IsMajor)
    
    $existingBackups = Get-ChildItem -Path $BackupDir -Directory | Where-Object { 
        $_.Name -match "$ProjectName-v(\d+)\.(\d+)$" 
    }
    
    if ($existingBackups.Count -eq 0) {
        return "v1.0"
    }
    
    # Parse version numbers and find the highest
    $versions = $existingBackups | ForEach-Object {
        if ($_.Name -match "$ProjectName-v(\d+)\.(\d+)$") {
            [PSCustomObject]@{
                Major = [int]$matches[1]
                Minor = [int]$matches[2]
                FullVersion = "$($matches[1]).$($matches[2])"
            }
        }
    } | Sort-Object Major, Minor
    
    $latest = $versions | Select-Object -Last 1
    
    if ($IsMajor) {
        $newMajor = $latest.Major + 1
        $newMinor = 0
    } else {
        $newMajor = $latest.Major
        $newMinor = $latest.Minor + 1
    }
    
    return "v$newMajor.$newMinor"
}

# Get the next version
$version = Get-NextVersion -BackupDir $BackupPath -IsMajor $Major
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupName = "$ProjectName-$version"
$backupFullPath = Join-Path $BackupPath $backupName

Write-Host "Creating backup: $backupName" -ForegroundColor Cyan
Write-Host "Timestamp: $timestamp" -ForegroundColor Gray
Write-Host "Source: $SourcePath" -ForegroundColor Gray
Write-Host "Destination: $backupFullPath" -ForegroundColor Gray

@"
    $robocopyArgs += "/XD"
    $robocopyArgs += "node_modules"
    $robocopyArgs += ".git"
    $robocopyArgs += ".vs"
    
    # Run robocopy
    $result = Start-Process -FilePath "robocopy" -ArgumentList $robocopyArgs -Wait -PassThru -NoNewWindow
        throw "Robocopy failed with exit code: $($result.ExitCode)"
    }
    
    # Create a backup info file
    $backupInfo = @{
        BackupName = $backupName
        Version = $version
        Timestamp = $timestamp
        SourcePath = $SourcePath.Path
    $backupInfoPath = Join-Path $backupFullPath "BACKUP_INFO.json"
    $backupInfo | ConvertTo-Json -Depth 3 | Out-File -FilePath $backupInfoPath -Encoding UTF8
    
    # Create a README file
    $readmeContent = @"
# Website Backup: $backupName

**Backup Created:** $timestamp
**Version:** $version
**Source:** $($SourcePath.Path)

## Backup Contents
- Files: $($backupInfo.FileCount)
- Folders: $($backupInfo.FolderCount)
- Total Size: $($backupInfo.TotalSize) MB

## Restore Instructions
To restore this backup:
1. Copy all contents from this folder to your desired location
2. Ensure all file permissions are set correctly
3. Update any absolute paths if necessary

## Changes Log
This backup was created after implementing:
- Mobile menu refinements and CSS cleanup
- Canonical tag coverage for all pages
- Honeypot spam protection
- Performance optimizations (image dimensions, script deferring)
- JSON-LD structured data for all service pages
- Comprehensive accessibility improvements (A11y)
  - Visible focus styles for all interactive elements
  - Enhanced color contrast in dark mode
  - Keyboard-dismissable modals with Esc key support
  - ARIA labels and semantic roles
  - WCAG 2.1 AA compliance

For technical questions, contact the development team.
"@
    
    $readmePath = Join-Path $backupFullPath "README.md"
    $readmeContent | Out-File -FilePath $readmePath -Encoding UTF8
    
    Write-Host "✅ Backup completed successfully!" -ForegroundColor Green
    Write-Host "📁 Location: $backupFullPath" -ForegroundColor Green
    Write-Host "📊 Files: $($backupInfo.FileCount) | Folders: $($backupInfo.FolderCount) | Size: $($backupInfo.TotalSize) MB" -ForegroundColor Green
    
    # List recent backups
    Write-Host "`n📋 Recent Backups:" -ForegroundColor Yellow
    Get-ChildItem -Path $BackupPath -Directory | Where-Object { 
        $_.Name -match "$ProjectName-v\d+\.\d+$" 
    } | Sort-Object Name -Descending | Select-Object -First 5 | ForEach-Object {
        $size = [math]::Round((Get-ChildItem -Path $_.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
        Write-Host "  $($_.Name) - $size MB - $($_.CreationTime)" -ForegroundColor Gray
    }
    
} catch {
    Write-Error ("Backup failed: " + $_.Exception.Message)
    # Clean up failed backup folder if it exists
    if (Test-Path $backupFullPath) {
        Remove-Item -Path $backupFullPath -Recurse -Force
    }
    exit 1
}



*** End Patch
  - Enhanced color contrast in dark mode
