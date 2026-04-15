# 设置输入和输出路径
$inputDir = "D:\origin\recv\rm"
$repairedDir = "C:\temp\fixed\repaired_results"
$corruptedDir = "C:\temp\fixed\corrupted_trash"

# 创建文件夹
if (!(Test-Path $repairedDir)) { New-Item -ItemType Directory -Path $repairedDir }
if (!(Test-Path $corruptedDir)) { New-Item -ItemType Directory -Path $corruptedDir }

# 遍历文件夹中的所有文件
Get-ChildItem -Path $inputDir -File | ForEach-Object {
    $currFile = $_.FullName
    $outFile = Join-Path $repairedDir ($_.BaseName + ".mp4")
    
    Write-Host "正在检测: $($_.Name)..." -ForegroundColor Cyan

    # 调用 ffmpeg 进行强制转码测试 (只取前5秒以节省时间)
    #& ffmpeg -y -i $currFile -t 5 -c:v libx264 -c:a aac -strict experimental $outFile 2>$null

    # -err_detect ignore_err: 强行跳过损坏的数据块
    # -reconnect 1: 如果是网络或流式文件尝试重连（对本地文件也有一定稳定作用）
    # -preset superfast: 提高处理几千个文件的效率
    & ffmpeg -y -i $currFile -err_detect ignore_err -c:v libx264 -c:a aac -preset superfast $outFile 2>$null
    
    # 检查 FFmpeg 的退出代码 ($LASTEXITCODE)
    if ($LASTEXITCODE -eq 0) {
        Write-Host "成功！文件有救，已存入 repaired_results" -ForegroundColor Green
    } else {
        Write-Host "失败！文件彻底损坏，移至 corrupted_trash" -ForegroundColor Red
        Move-Item -Path $currFile -Destination $corruptedDir -Force
        if (Test-Path $outFile) { Remove-Item $outFile } # 删除失败生成的空文件
    }
}