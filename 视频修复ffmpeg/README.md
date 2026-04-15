FFmpeg “暴力”救活方案
***

#1. 强制转码（不只是复制，而是重编）  
CMD 或 Powershell
```
ffmpeg -i "D:\origin\recv\rm\f124888263.rm" -f mp4 -vcodec libx264 -acodec aac "C:\temp\fixed\f124888263.mp4"
```

如果可以修复，则说明文件值得抢救
***

#2. 自动化筛查脚本  
Powershell脚本：  
遍历文件夹，尝试将每个文件转码为极小的 MP4。  

  ·成功：说明文件数据流基本完整，移动到 可修复 文件夹。  
  ·失败：说明是彻底的乱码或空数据，移动到 损坏 文件夹。
```
ffrepaire.ps1
```

处理逻辑拆解:  
  对于“好文件” (FFmpeg 转码成功)：  
  它会执行完整的重编码（从头到尾）。  
  在 $repairedDir（即 C:\temp\fixed\repaired_results）目录下生成一个新的 .mp4 文件。  
  *注意：原始的 .rm 文件会留在原处（D:\origin\recv\rm），不会被移动。  
  
  对于“坏文件” (FFmpeg 转码报错)：  
  它会判定该文件无法救活。  
  执行 Move-Item，将原始的 .rm 文件从原文件夹彻底移动到 $corruptedDir。  
  同时清理掉转码失败产生的 0 字节或破损的临时 mp4。
