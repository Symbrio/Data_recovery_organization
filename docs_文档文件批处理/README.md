文档文件批处理
***
1. 可读性(筛选废片)
   首先，我们要区分哪些文件是“能打开的”，哪些是“物理损坏”的。
1.1 PDF 检查
使用 pdfinfo 工具。如果文件损坏，它会直接报错。
```
# 批量检查并记录损坏文件
find /path/to/pdfs -name "*.pdf" -exec sh -c 'pdfinfo "{}" > /dev/null 2>&1 || echo "{}"' \; > broken_pdfs.txt
```
1.2 Office 文档 (doc/docx/xls/xlsx/ppt/pptx)
现代的 Office 文件（docx/xlsx/pptx）本质上是 ZIP 压缩包。如果 ZIP 结构坏了，文件肯定打不开。
```
# 检查 docx/xlsx/pptx 是否完整
find . -regex ".*\(docx\|xlsx\|pptx\)" -exec sh -c 'unzip -t "{}" > /dev/null 2>&1 || echo "{}"' \; > broken_office.txt
```
***
2. 快速阅览大意 (文本透视)
   不需要打开 Word 或 PDF，只需要把里面的纯文字“抽出来”看一眼。
2.1 Apache Tika (文档扫描器)
   专业数据恢复和取证领域的标配工具。它支持 1400 多种格式，能直接把文档里的文字吐出来。
2.1.1 安装： 在 Ubuntu 上安装 tika-app 的 jar 包。
```
https://www.apache.org/dyn/closer.lua/tika/3.3.0/tika-app-3.3.0.jar
```
2.1.2 批量预览： 命令行“高亮预览”脚本 (无须生成文件)
```
# 进入你的 doc 目录
cd /media/sym/SymbrioHDD/origin/recv/doc

# 运行以下组合命令
for f in *; do
    echo -e "\033[1;32m--- FILE: $f ---\033[0m"
    # 2>/dev/null 屏蔽所有 Java 警告日志
    # head -n 5 只看前五行，通常包含标题或开头
    java -jar /home/sym/Downloads/tika-app-3.3.0.jar -t "$f" 2>/dev/null | head -n 5
    echo ""
done
```
*注：使用实际的 jar 包绝对路径：/home/sym/Downloads/tika-app-3.3.0.jar

2.2 文档内容自动重命名脚本
执行前的准备：
1. 确保安装了 exiftool: sudo apt install libimage-exiftool-perl。
2. 修改脚本顶部的 TIKA_JAR、SRC_DIR 和 DEST_DIR 路径。
3. 可以先在 doc 文件夹里放 3-5 个文件做一个小测试。
4. 预期生成的名称： 关于2026年市场调研报告_20260409.doc
```
#auto rename
import os
import json
import subprocess
import re
from datetime import datetime

# --- 配置区 ---
TIKA_JAR = "/home/sym/Downloads/tika-app-3.3.0.jar"  # 替换为你实际的 tika 路径
SRC_DIR = "/media/sym/SymbrioHDD/origin/recv/doc" # 你的源文件目录
DEST_DIR = "/media/sym/SymbrioHDD/rename/renamed_docs" # 重命名后的存放目录
os.makedirs(DEST_DIR, exist_ok=True)

def get_clean_text(text):
    """提取前20个字符并清理掉不能作为文件名的特殊字符"""
    # 过滤掉换行符和多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    # 截取前20个字符
    short_text = text[:20]
    # 替换掉 Windows/Linux 文件名不允许的特殊字符
    short_text = re.sub(r'[\\/:*?"<>|]', '_', short_text)
    return short_text

def get_creation_date(file_path):
    """通过 exiftool 获取创作时间，如果没有则用修改时间"""
    try:
        cmd = ["exiftool", "-j", "-CreateDate", "-ModifyDate", file_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        meta = json.loads(res.stdout)[0]
        # 优先取创建时间，其次取修改时间
        date_str = meta.get("CreateDate") or meta.get("ModifyDate")
        if date_str:
            # 将 exiftool 的格式 "2024:03:09 15:42:00" 转为 "20240309"
            dt = datetime.strptime(date_str[:10], "%Y:%m:%d")
            return dt.strftime("%Y%m%d")
    except:
        pass
    return "UnknownDate"

def process_files():
    for filename in os.listdir(SRC_DIR):
        if filename.startswith('.'): continue
        
        old_path = os.path.join(SRC_DIR, filename)
        ext = os.path.splitext(filename)[1]
        
        print(f"正在处理: {filename}...")
        
        # 1. 使用 Tika 抓取内容
        try:
            # -t 提取文本，head -n 5 确保只拿开头
            content = subprocess.check_output(
                f"java -jar {TIKA_JAR} -t '{old_path}' 2>/dev/null | head -n 5", 
                shell=True, text=True
            )
            if not content.strip():
                content = "EmptyContent"
        except:
            content = "UnreadableFile"

        # 2. 格式化前缀和日期
        name_prefix = get_clean_text(content)
        date_suffix = get_creation_date(old_path)
        
        # 3. 构造新文件名: 抓取内容_日期.扩展名
        new_filename = f"{name_prefix}_{date_suffix}{ext}"
        new_path = os.path.join(DEST_DIR, new_filename)

        # 防止重名
        counter = 1
        while os.path.exists(new_path):
            new_path = os.path.join(DEST_DIR, f"{name_prefix}_{date_suffix}_{counter}{ext}")
            counter += 1

        # 执行复制（建议先复制而非直接重命名，更安全）
        subprocess.run(["cp", old_path, new_path])
        print(f"✅ 已重命名为: {os.path.basename(new_path)}")

if __name__ == "__main__":
    process_files()
```
*注：
  1. python 的字符串切片 [:20] 原生支持中文字符统计，不会出现乱码或半个字符的情况。
  2. 特殊字符过滤：文档第一行经常包含 /、: 等字符，如果直接重命名会报错，脚本里的 get_clean_text 自动把它们换成了下划线。
  3. 复制模式：脚本使用 cp 而不是 mv。这样如果重命名效果不理想，你的原始文件 f12345.doc 依然还在。
  4. 时间校准：调用 exiftool 读取文档内部嵌入的创建时间（但绝大部分为 UnknownDate 可考虑省略）。
  

   
