<#
.SYNOPSIS
    Automated Windows Setup Helper Script for GitHub Profile README (kalpshah/kalpshah)
.DESCRIPTION
    Replaces username/name placeholders across README.md and workflow files,
    installs Python dependencies, and runs all generators in one go.
#>

param (
    [string]$Username = "K1905-cpu",
    [string]$Name = "Kalp Shah",
    [string]$Image = "..\public\me.jpg",
    [switch]$Circle
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Building GitHub Profile Assets for $Name ($Username)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Install Pillow
Write-Host "[1/4] Installing Python dependency (pillow)..." -ForegroundColor Yellow
python -m pip install pillow --quiet

# 2. Replace Placeholders in README.md and Workflows
Write-Host "[2/4] Updating placeholders in README.md and .github/workflows..." -ForegroundColor Yellow

$FilesToUpdate = @(
    "README.md",
    ".github/workflows/metrics.yml",
    ".github/workflows/snake.yml",
    ".github/workflows/radar.yml"
)

foreach ($file in $FilesToUpdate) {
    if (Test-Path $file) {
        (Get-Content $file) -replace 'YOUR_USERNAME', $Username -replace 'YOUR_NAME', $Name | Set-Content $file
    }
}

# 3. Generate Dot Portrait (if image exists)
Write-Host "[3/4] Generating Dot Matrix Portrait..." -ForegroundColor Yellow
if (Test-Path $Image) {
    $CircleFlag = if ($Circle) { "--circle" } else { "" }
    python scripts/dotify.py $Image -o assets/portrait --cols 100 --equalize --detail 0.5 --color $CircleFlag
} else {
    Write-Host "Note: Portrait source image '$Image' not found. Skipping dotify step for now." -ForegroundColor DarkYellow
    Write-Host "Drop your photo in the folder and run: python scripts/dotify.py me.png -o assets/portrait --cols 100 --equalize --detail 0.5 --color" -ForegroundColor DarkGray
}

# 4. Generate Radars & Cards
Write-Host "[4/4] Generating Radar Charts & Project Cards..." -ForegroundColor Yellow
python scripts/radar.py --data assets/skills.json -o assets/radar
python scripts/radar.py --github $Username -o assets/radar-langs --limit 7 --values --curve 0.4 --exclude "shell,html,css,makefile,dockerfile,batchfile,procfile"
python scripts/cards.py --user $Username --out assets

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Setup complete! Open preview.html in your browser to inspect." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
