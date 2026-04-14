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