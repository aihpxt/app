$gitPath = "C:\Program Files\Git\bin\git.exe"
$workDir = "D:\aiphxt-app"

Write-Host "Step 1: Delete old .git..."
$gitDir = Join-Path $workDir ".git"
if (Test-Path $gitDir) {
    Remove-Item -Path $gitDir -Recurse -Force
    Write-Host "  Deleted"
}

Write-Host "Step 2: Git init..."
Set-Location $workDir
& $gitPath init

Write-Host "Step 3: Add files..."
& $gitPath add -A

Write-Host "Step 4: Check large files..."
$largeFiles = @()
& $gitPath ls-files | ForEach-Object {
    $f = Join-Path $workDir $_
    if (Test-Path $f) {
        $sz = (Get-Item $f).Length
        if ($sz -gt 50MB) {
            $mb = [math]::Round($sz/1MB,2)
            $largeFiles += "$mb MB - $_"
        }
    }
}

if ($largeFiles.Count -gt 0) {
    Write-Host "WARNING: Large files found:" -ForegroundColor Red
    foreach ($lf in $largeFiles) {
        Write-Host "  $lf" -ForegroundColor Red
    }
    exit 1
} else {
    Write-Host "OK - No large files"
}

Write-Host "Step 5: Commit..."
& $gitPath commit -m "Initial commit"

Write-Host "Step 6: Add remote origin..."
& $gitPath remote add origin "https://github.com/aihpxt/app.git"

Write-Host ""
Write-Host "Done! Now run push: & '$gitPath' push -u origin main"
