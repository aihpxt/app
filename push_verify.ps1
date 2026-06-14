$gitPath = "C:\Program Files\Git\bin\git.exe"
$workDir = "D:\aiphxt-app"

Write-Host "=== Attempting git push ===" -ForegroundColor Green
& $gitPath -C $workDir push -u origin main
$exitCode = $LASTEXITCODE
Write-Host ""
Write-Host "Exit code: $exitCode" -ForegroundColor Yellow

if ($exitCode -ne 0) {
    Write-Host ""
    Write-Host "Push failed. Common reasons:" -ForegroundColor Red
    Write-Host "  1. GitHub authentication required (need Personal Access Token or SSH key)"
    Write-Host "  2. Repository does not exist at https://github.com/aihpxt/app.git"
    Write-Host "  3. Network connectivity issue"
    Write-Host ""
    Write-Host "To fix, try using a Personal Access Token in the URL:" -ForegroundColor Yellow
    Write-Host "  git remote set-url origin https://YOUR_TOKEN@github.com/aihpxt/app.git"
    Write-Host ""
    Write-Host "Or create the repository first at: https://github.com/new"
} else {
    Write-Host "=== Push successful! ===" -ForegroundColor Green
}
