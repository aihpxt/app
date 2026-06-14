$workDir = "D:\aiphxt-app"
$gitPath = "C:\Program Files\Git\bin\git.exe"

Write-Host "=== Step 1: Check large files in the project ===" -ForegroundColor Green
Get-ChildItem -Path $workDir -Recurse -File | 
    Where-Object { $_.Length -gt 10MB } | 
    Sort-Object Length -Descending | 
    Select-Object FullName, @{Name="SizeMB";Expression={[math]::Round($_.Length/1MB,2)}} |
    Format-Table -AutoSize

Write-Host ""
Write-Host "=== Step 2: Check current git files ===" -ForegroundColor Green
& $gitPath -C $workDir ls-tree -r --name-only HEAD | Select-Object -First 50
