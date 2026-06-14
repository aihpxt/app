$gitPath = "C:\Program Files\Git\bin\git.exe"
$workDir = "D:\aiphxt-app"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Git Repository Clean Re-initialization" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== Step 1: Delete old .git directory ===" -ForegroundColor Yellow
$gitDir = Join-Path $workDir ".git"
if (Test-Path $gitDir) {
    Remove-Item -Path $gitDir -Recurse -Force
    Write-Host "  Old .git directory deleted"
} else {
    Write-Host "  No .git directory found"
}

Write-Host ""
Write-Host "=== Step 2: Initialize new git repo ===" -ForegroundColor Green
Set-Location $workDir
& $gitPath init
Write-Host "  Git repo initialized"

Write-Host ""
Write-Host "=== Step 3: Verify .gitignore is in place ===" -ForegroundColor Green
if (Test-Path (Join-Path $workDir ".gitignore")) {
    Write-Host "  .gitignore found"
    Get-Content (Join-Path $workDir ".gitignore") | Select-Object -First 5
    Write-Host "  ... (rest omitted)"
} else {
    Write-Host "  WARNING: .gitignore not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Step 4: Add files (respecting .gitignore) ===" -ForegroundColor Green
& $gitPath add -A
Write-Host "  Files added"

Write-Host ""
Write-Host "=== Step 5: Check files being committed ===" -ForegroundColor Green
$statusOutput = & $gitPath status --short
$statusOutput | Select-Object -First 30
Write-Host "  ..."

Write-Host ""
Write-Host "=== Step 6: Verify no large files > 50MB ===" -ForegroundColor Yellow
$largeFiles = & $gitPath ls-files | ForEach-Object {
    $file = $_
    if (Test-Path (Join-Path $workDir $file)) {
        $size = (Get-Item (Join-Path $workDir $file)).Length
        if ($size -gt 50MB) {
            "$([math]::Round($size/1MB,2) MB - $file"
        }
    }
}
if ($largeFiles) {
    Write-Host "  WARNING: Large files detected:" -ForegroundColor Red
    $largeFiles | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
    Write-Host ""
    Write-Host "  Adding them to .gitignore and retrying..." -ForegroundColor Yellow
} else {
    Write-Host "  OK - No files over 50MB" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Step 7: Commit ===" -ForegroundColor Green
& $gitPath commit -m "Initial commit"
Write-Host "  Commit done"

Write-Host ""
Write-Host "=== Step 8: Add remote origin ===" -ForegroundColor Green
& $gitPath remote add origin "https://github.com/aihpxt/app.git"
Write-Host "  Remote added"

Write-Host ""
Write-Host "=== Step 9: Verify repo summary ===" -ForegroundColor Cyan
Write-Host "  Log:"
& $gitPath log --oneline -3
Write-Host ""
Write-Host "  Remote:"
& $gitPath remote -v
Write-Host ""
Write-Host "  Branch:"
& $gitPath branch -v

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Ready to push. Now run the push command:" -ForegroundColor Yellow
Write-Host "  & '$gitPath' push -u origin main" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
