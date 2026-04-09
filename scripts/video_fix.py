import json
import os
import subprocess

# --- 配置区 ---
JSON_FILE = 'results_broken_files_compact.json'  # 你的JSON文件名
OUTPUT_BASE = '/home/sym/temp/fixed_videos' # 修复后的存放路径
FFMPEG_PATH = 'ffmpeg' # 如果系统路径没问题保持默认

def repair_videos():
    # 创建输出目录
    fixed_dir = os.path.join(OUTPUT_BASE, 'fixed')
    failed_dir = os.path.join(OUTPUT_BASE, 'failed')
    os.makedirs(fixed_dir, exist_ok=True)
    os.makedirs(failed_dir, exist_ok=True)

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 如果JSON是一个列表直接迭代，如果是字典包含列表请修改此处
    files = data if isinstance(data, list) else data.get('files', [])

    for entry in files:
        input_path = entry['path']
        if not os.path.exists(input_path):
            print(f"跳过：文件不存在 -> {input_path}")
            continue

        file_name = os.path.basename(input_path)
        # 为了防止同名冲突，给输出文件名加个前缀或后缀
        output_path = os.path.join(fixed_dir, f"fixed_{file_name}")

        print(f"正在尝试修复: {file_name} ...")
        
        '''
        # 执行 ffmpeg 快速修复命令
        # -y: 自动覆盖已存在的输出文件
        # -loglevel error: 只显示错误信息，保持终端干净
        cmd = [
            FFMPEG_PATH, '-y', '-loglevel', 'error',
            '-i', input_path,
            '-c', 'copy', '-map', '0',
            output_path
        ]
        '''

        # --- 执行 FFmpeg 重编吗命令 ---
        # -c:v libx264: 使用 H.264 编码器
        # -crf 28: 质量参数（23-28 之间，数字越大文件越小，质量稍降，适合抢救）
        # -preset fast: 编码速度预设
        # -c:a aac: 音频转为常规 AAC 格式
        # -ignore_unknown: 忽略无法识别的数据流（如损坏的字幕轨道）
        
        cmd = [
            FFMPEG_PATH, '-y', '-loglevel', 'error',
            '-ignore_unknown', 
            '-i', input_path,
            '-c:v', 'libx264', '-crf', '28', '-preset', 'fast',
            '-c:a', 'aac', '-strict', 'experimental',
            '-map', '0',
            output_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ 成功: {output_path}")
            else:
                print(f"❌ 失败: {file_name} (ffmpeg 无法解析)")
                # 如果失败了，记录到日志或移动标记
                with open('repair_log.txt', 'a') as log:
                    log.write(f"FAILED: {input_path}\nError: {result.stderr}\n---\n")
        except Exception as e:
            print(f"⚠️ 脚本错误: {str(e)}")

if __name__ == "__main__":
    repair_videos()