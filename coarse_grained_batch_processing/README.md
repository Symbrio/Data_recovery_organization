粗粒度文件筛选：批量文件识别/去重（PowerShell）  

# 一、核心方法论（必须掌握）

```
分类 → 删除**“不需要的”**文件类型 → 按文件类型储存 → 去重
```

---

# 二、各流程脚本

```
ext_check.ps1 → duplication_check.ps1 → duplication_remove.ps
```

## 1️⃣ 分类：ext_check

- ext_check.ps1储存与：onedrive/usefulscript/,,,/ext_check.ps1
    - **以下原草稿为参考*

```powershell
#识别所有文件类型并统计数量
#Get-ChildItem -Recurse -File | Group-Object Extension | Sort Count -Descending

$path = "e:\origin\recv\recv4"

$less10 = "E:\nonsence_check_recv4\less10kb"
$wasted = "E:\nonsence_check_recv4\10upwasted"
$unknown = "E:\nonsence_check_recv4\unknown"

# 创建目录（如果不存在）
New-Item -ItemType Directory -Force -Path $less10 | Out-Null
New-Item -ItemType Directory -Force -Path $wasted | Out-Null
New-Item -ItemType Directory -Force -Path $unknown | Out-Null

# 无意义类型
$wastedExt = @(
".html",".txt",".xml",".svg",".swc"
)

# 常见保留类型（文档/图片/影音/压缩包）
$keepExt = @(
".bmp",".jpg",".jpeg",".png",".gif",".heic",".webp",".tiff",
".cr2",".cr3",".arw",".dng",".pef",".ptx",".rw2",".raf",
".pdf",".doc",".docx",".ppt",".pptx",".xls",".xlsx",
".mp4",".mov",".avi",".mkv",".wmv",".flv",".mp3",".wav",".m4a",".aac",".flac",".rm",
".rar",".zip",".7z",".001"
)

Get-ChildItem -Path $path -Recurse -File | ForEach-Object {

    $file = $_
    $ext = $file.Extension.ToLower()
    $size = $file.Length

    # 1 小于10KB
    if ($size -lt 10KB) {
        Move-Item $file.FullName -Destination $less10 -Force
        Write-Host "Moved <10KB:" $file.FullName
        return
    }

    # 2 大于10KB且无意义类型
    if ($wastedExt -contains $ext) {
        Move-Item $file.FullName -Destination $wasted -Force
        Write-Host "Moved wasted:" $file.FullName
        return
    }

    # 3 不是常见文档图片影音
    if (-not ($keepExt -contains $ext)) {
        Move-Item $file.FullName -Destination $unknown -Force
        Write-Host "Moved unknown:" $file.FullName
    }

}
```

---

## 2️⃣ 去重Hash计算：duplication_check

### 两阶段算法（关键）

```
Step1: 按文件大小分组
Step2: 对相同大小文件计算 Hash
```

原因：

```
不同大小 = 不可能相同
→ 减少 90% Hash 计算
```

---

- duplication_check.ps1储存与：onedrive/usefulscript/…/duplication_check.ps1
    - **以下原草稿为参考*

```powershell
$root = "E:\origin\h"

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
        }
    }
}

$duplicates | Export-Csv "E:\duplicates.csv" -NoTypeInformation -Encoding UTF8
```

---

## 3️⃣ 去重（保留一个）：duplication_remove

- duplication_remove.ps1储存与：onedrive/usefulscript/…/duplication_remove.ps1
    - **以下原草稿为参考*

```powershell
$csv = "E:\duplicates.csv"
$trash = "E:\duplicate_trash"

New-Item -ItemType Directory -Force -Path $trash | Out-Null

$data = Import-Csv $csv

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

        Move-Item -LiteralPath $_.FullName -Destination $dest -WhatIf:$false
    }
}
```

---

# 三、关键注意事项（避免踩坑）

## 1️⃣ PowerShell WhatIf 问题

```powershell
$WhatIfPreference = $false
```

或：

```powershell
Move-Item -WhatIf:$false
```

---

## 2️⃣ CSV 读取问题

```
Export-Csv 默认是逗号分隔
→ Import-Csv 不要写 -Delimiter
```

---

## 3️⃣ 路径安全

始终使用：

```powershell
-LiteralPath
```

避免中文或特殊字符问题。

---

## 4️⃣ 不要直接删除

推荐：

```
移动到 trash 目录
```

---

# 四、可扩展优化方向

未来可升级：

- 多线程 Hash
- 自动损坏图片检测
- 自动分类（photos/videos/docs）
- 空间节省统计
- GUI 工具辅助（AllDup 等）

---
