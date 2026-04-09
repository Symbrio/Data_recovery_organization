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
