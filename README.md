Data_recovery_organization

HDD数据恢复 --> 粗粒度去重去损 --> 细粒度相似识别 --> 内容识别 --> 文件批处理Toolkit

***

#Skeleton
```
├── hdd_recovery/                      # 分区、格式、数据恢复
  ├── testdisk & photorec的使用方法
├── coarse_grained_deduplication/      # 非常用格式筛选，相同文件去重
  ├── 筛选逻辑和方法
  ├── deduplication_check.ps1          # 先检查格式、重复
  ├── deduplication_remove.ps1         # 批处理文件
├── fine_grained_similarity/           # 筛选相似文件（如：缩略图，重复储存文件）
  ├──C zkawka (ubuntu)使用方法          #Czkawka 是一款免费、开源且运行速度极快的电脑多功能文件清理与去重工具
├── docs_文档文件批处理/                 # 文档文件内容速览及重命名
  ├── pdfinfo 和 TIKA的使用方法
  ├── auto_rename_tika.py               # 用TIKA提取内容，依据内容命名，ms文档/pdf/zip/rar,##Apache Tika 是一个开源的万能文件内容分析与数据提取工具包，可以通过统一的接口从超过 1000 种文件格式（如 PDF、Word、Excel、PPT、图片等）中检测并提取文本和元数据。
├── 视频修复ffmpeg
  ├── ffmpeg使用方法
  ├── ffrepaire.ps1                     # 分类ff可以救的视频文件并重新编码，分拣出彻底损坏文件
├── .gitignore                          # TBD
└── README.md
```

***

###当前任务
- [ ] 完善 `.gitignore` 以排除大型镜像文件
- [ ] 导入notion笔记
- [ ] 上传useful script
- [ ] 

***

