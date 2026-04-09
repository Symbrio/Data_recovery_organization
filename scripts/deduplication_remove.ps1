$csv = "E:\duplicates_recv.csv"   #哈希列表路径设置！！！
$trash = "E:\origin\duplicate_recv_trash"

New-Item -ItemType Directory -Force -Path $trash | Out-Null

$data = Import-Csv $csv | Where-Object { $_.Path -and $_.Path.Trim() -ne "" }

$data | Group-Object Hash | ForEach-Object {

    $files = $_.Group |
        Where-Object { Test-Path $_.Path } |
        ForEach-Object { Get-Item $_.Path } |
        Sort-Object LastWriteTime -Descending

    if ($files.Count -lt 2) { return }

    $files | Select-Object -Skip 1 | ForEach-Object {

        $dest = Join-Path $trash $_.Name

        $i = 1
        while (Test-Path $dest) {
            $dest = Join-Path $trash ($_.BaseName + "_$i" + $_.Extension)
            $i++
        }

        Move-Item $_.FullName $dest #-WhatIf <# -WhatIf 指令是测试指令是否可运行，有无报错，实际运行时需注释掉 #>
        Write-Host "Moved:" $_.FullName #-WhatIf
    }
}