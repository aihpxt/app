$gitPath = "C:\Program Files\Git\bin\git.exe"

Set-Location "D:\aiphxt-app"

Write-Host "=== Step 1: Create README.md ===" -ForegroundColor Green
if (-not (Test-Path "README.md")) {
    Set-Content -Path "README.md" -Value "# app" -Encoding UTF8
    Write-Host "README.md created"
} else {
    Write-Host "README.md already exists"
}

Write-Host "=== Step 2: git init ===" -ForegroundColor Green
if (-not (Test-Path ".git")) {
    & $gitPath init
} else {
    Write-Host "Git repo already initialized"
}

Write-Host "=== Step 3: git add README.md ===" -ForegroundColor Green
& $gitPath add README.md

Write-Host "=== Step 4: git commit -m 'first commit' ===" -ForegroundColor Green
& $gitPath -c user.email="user@example.com" -c user.name="User" commit -m "first commit"

Write-Host "=== Step 5: git branch -M main ===" -ForegroundColor Green
& $gitPath branch -M main

Write-Host "=== Step 6: git remote add origin ===" -ForegroundColor Green
$remotes = & $gitPath remote
if ($remotes -contains "origin") {
    Write-Host "Remote 'origin' already exists, updating URL..."
    & $gitPath remote set-url origin "https://github.com/aihpxt/app.git"
} else {
    & $gitPath remote add origin "https://github.com/aihpxt/app.git"
}

Write-Host "=== Step 7: git push -u origin main ===" -ForegroundColor Green
Write-Host "Note: This requires GitHub authentication. Make sure the repository exists at GitHub." -ForegroundColor Yellow
& $gitPath push -u origin main

Write-Host "=== Done! ===" -ForegroundColor Green
