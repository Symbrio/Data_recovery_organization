细粒度文件筛选：损坏识别/去重/相似  

# 一、Windows平台

图片：ImageMagick ***未尝试**

---

# 二、Ubuntu平台

## 1️⃣ Czkawka安装

Releases 版本选择

```
https://github.com/qarmin/czkawka/releases

GUI:
linux_czkawka_gui_x86_64
linux_czkawka_gui_heif_raw_x86_64

CLI
linux_czkawka_cli_x86_64
linux_czkawka_cli_heif_raw_x86_64
```

已尝试*linux_czkawka_gui_x86_64*

！Heif_raw问题待测试

```
chmod +x linux_czkawka_gui_x86_64
# 如果遇到权限问题（无法读取外部硬盘或报错），使用 sudo 启动
sudo ./linux_czkawka_gui_x86_64
```

- **挂载注意：** exFAT/NTFS 硬盘若显示文件不全，先在 Win11 下“安全弹出”或在 Ubuntu 下运行 `ls -R | wc -l` 确认系统已识别全部文件。

```
ls -R /media/sym/SymbrioHDD/origin/recv/ | wc -l
```

- *`ls -l`为当前目录；`ls -R`为递归（遍历）

---

## 2️⃣ 清理方法论

```
Hash检查重复 → 错误的扩展 → 损坏的文件 → 重复的音乐 → 相似的视频 → 相似的图像
```

---

## 3️⃣ Hash检查重复

1. **添加路径：** 在 `Included Directories` 添加目标文件夹，确保勾选 **Recursive** (递归)。单文件夹去重时绝对不要勾选`Reference Folder (参考文件夹)`
2. **清理干扰：**
    - 清空 `Excluded Items` (防止跳过某些备份目录)。
    - 清空 `Allowed Extensions` (除非你只想扫某一种格式)。
    - **权限墙：** 看到文件但搜出 0 组，通常是由于 `exFAT` 挂载权限导致程序无法读取文件内部字节，需用 `chmod 777` 或 `sudo` 运行。
    - **硬链接排除：**如果文件是通过某些备份工具产生的，它们可能是“硬链接”。在文件系统看来，它们指向同一个物理数据块。在 `Duplicate Files` 选项卡下方，**取消勾选** `Ignore hard links`。
3. **配置参数：** 将 `Min file size` 设为 **0**，关闭 `Settings` 中的 `Use Cache` (确保数据最新)。
4. **执行搜索：** 点击 **Search**。
    - *闪退/秒停：* 检查权限或文件大小是否全部唯一。
    - *进度条慢：* 正常现象，正在计算 Hash 或解码图片。
5. 扫描完成后，使用底部的 **Select** 按钮进行批量勾选：
- **保留最初版本：** `Select` -> `All except oldest` (除了最旧的全部选中)。
- **保留最高质量：**
    - 音乐：`Select` -> `All except biggest` (码率通常最高)。
    - 图片：根据预览图，手动确认或选 `All except biggest`。
- **安全执行：**
    - **Delete:** 直接删除。
    - **Move:** (推荐) 移动到专门的 `To_Be_Deleted` 文件夹，确认无误后再清空。
    - **Hardlink:** 物理省空间，但在原位置保留文件记录。

---

## 4️⃣ 损坏的文件

---

## 5️⃣ 重复音乐

1. **内容，取样，计算对比 →** 会按组分类
2. **保留最高质量：**
    - 音乐：`Select` -> `All except biggest` (码率通常最高)。

---

## 6️⃣ 相似视频

1. **内容，取样，计算对比 →** 会按组分类
2. 在删除之前，尝试用 ffmpeg 重新封装（Remux）或强制重新编码
3. **保留最高质量：**
    
---

## 7️⃣ 损坏的图片  

🛠️ 推荐的操作流 (SOP)
参数设置：<img width="512" height="372" alt="unnamed" src="https://github.com/user-attachments/assets/ee4b118f-74fb-4e1d-bb9b-5fe5bd715d78" />

```
标签页：选左侧 Similar Images。
添加路径：/media/sym/SymbrioHDD/origin/recv/jpg。

调整算法 (Resize Algorithm)：Lanczos3 (这是目前最细腻的缩放算法，能保证指纹提取的准确性)
哈希类型 (Hash Type)：Gradient（梯度哈希,光影变化敏感）
相似性 (Similarity)：2+
哈希大小 (Hash Size)：16(数值越大（如 32/64）越精准，但极易因为图片边缘的一点点损坏（比如多了一行黑边）而判定为不相似。16 是平衡性能与兼容性的黄金值)
项目配置 (Project Configuration)\最小大小 (Min Size) 过滤：0
```

---

# 三、关键注意事项（避免踩坑）  
图片相似性靠近40时，连拍会被认作相似

---
