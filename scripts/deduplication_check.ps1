$root = "E:\origin\recv" #要检查的文件夹路径

$files = Get-ChildItem -Path $root -Recurse -File

$sizeGroups = $files | Group-Object Length | Where-Object { $_.Count -gt 1 }

$duplicates = @()

foreach ($group in $sizeGroups) {

    $hashGroups = $group.Group |
        Get-FileHash -Algorithm SHA256 |
        Group-Object Hash |
        Where-Object { $_.Count -gt 1 }

    foreach ($hg in $hashGroups) {
        foreach ($file in $hg.Group) {
            $duplicates += [PSCustomObject]@{
                Hash = $file.Hash
                Path = $file.Path
            }
            Write-Host "Processing:" $file.Path
        }
    }
}

# 导出 注意修改导出csv路径！！！
$duplicates | Export-Csv "E:\duplicates_recv.csv" -NoTypeInformation -Encoding UTF8