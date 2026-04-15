#auto rename
import os
import json
import subprocess
import re
from datetime import datetime

# --- 配置区 ---
TIKA_JAR = "/home/sym/Downloads/tika-app-3.3.0.jar"  # 替换为实际的 tika 路径
SRC_ROOT = "/media/sym/SymbrioHDD/origin/recv" # 源根目录
DEST_ROOT = "/media/sym/SymbrioHDD/rename" # 重命名后的存放根目录

# 新增：允许处理的文件后缀列表（全部小写，不带点）
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'rar', 'zip'
}

def get_clean_text(text):
    """提取前20个字并清理特殊字符"""
    if not text: return "EmptyContent"
    # 过滤换行、多余空格，取前20字符
    text = re.sub(r'\s+', ' ', text).strip()
    short_text = text[:20]
    # 过滤文件名非法字符
    short_text = re.sub(r'[\\/:*?"<>|]', '_', short_text)
    return short_text if short_text else "EmptyContent"

def get_creation_date(file_path):
    """通过 exiftool 获取文件内部真实的创作时间"""
    try:
        # 增加对 PDF 常用时间字段的抓取
        cmd = ["exiftool", "-j", "-CreateDate", "-DateTimeOriginal", "-ModifyDate", file_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        meta = json.loads(res.stdout)[0]
        # 优先级：创建时间 > 原始时间 > 修改时间
        date_str = meta.get("CreateDate") or meta.get("DateTimeOriginal") or meta.get("ModifyDate")
        if date_str:
            # 格式通常为 "2024:03:09 15:42:00"
            dt = datetime.strptime(date_str[:10], "%Y:%m:%d")
            return dt.strftime("%Y%m%d")
    except:
        pass
    return "UnknownDate"

def get_document_title(file_path):
    """针对 PDF 和 Office 文档，优先抓取 Tika 识别的 Title 元数据"""
    try:
        # 使用 -j 获取 JSON 格式的全元数据
        cmd = ["java", "-jar", TIKA_JAR, "-j", file_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        meta = json.loads(res.stdout)
        # 尝试获取各种可能的标题字段
        title = meta.get("dc:title") or meta.get("title") or meta.get("cp:subject")
        return title if title and len(str(title).strip()) > 1 else None
    except:
        return None

def process_all_files():
    # 递归遍历源根目录
    for root, dirs, files in os.walk(SRC_ROOT):
        for filename in files:
            if filename.startswith('.'): continue # 跳过隐藏文件
            
            old_path = os.path.join(root, filename)
            ext_raw = os.path.splitext(filename)[1].lower()
            ext = ext_raw[1:] if ext_raw.startswith('.') else "no_ext"

            # --- 新增筛选逻辑 ---
            if ext not in ALLOWED_EXTENSIONS:
                # print(f"跳过不支持的格式: {filename}")
                continue
            
            # 动态创建目标分类文件夹 (如 /rename/pdf, /rename/doc)
            target_sub_dir = os.path.join(DEST_ROOT, ext)
            os.makedirs(target_sub_dir, exist_ok=True)

            print(f"--- 正在处理: {filename} ---")

            # 1. 获取标题逻辑：优先元数据标题，其次正文前20字
            title_meta = get_document_title(old_path)
            if title_meta:
                name_prefix = get_clean_text(str(title_meta))
                print(f"   [元数据标题]: {name_prefix}")
            else:
                try:
                    # 抓取正文前 10 行来提取前缀
                    content = subprocess.check_output(
                        f"java -jar {TIKA_JAR} -t '{old_path}' 2>/dev/null | head -n 10", 
                        shell=True, text=True
                    )
                    name_prefix = get_clean_text(content)
                    print(f"   [正文提取]: {name_prefix}")
                except:
                    name_prefix = "Unreadable"

            # 2. 获取日期
            date_suffix = get_creation_date(old_path)
            
            # 3. 构造新文件名并处理重名
            new_filename = f"{name_prefix}_{date_suffix}{ext_raw}"
            new_path = os.path.join(target_sub_dir, new_filename)

            counter = 1
            while os.path.exists(new_path):
                new_path = os.path.join(target_sub_dir, f"{name_prefix}_{date_suffix}_{counter}{ext_raw}")
                counter += 1

            # 4. 执行复制
            try:
                subprocess.run(["cp", old_path, new_path])
                print(f"✅ 完成: {filename} -> {ext}/{os.path.basename(new_path)}")
            except Exception as e:
                print(f"❌ 失败: {filename}, 原因: {e}")

if __name__ == "__main__":
    process_all_files()
