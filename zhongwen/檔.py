from zhongwen.file import 抓取, 下載
from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

def 同步目錄(甲, 乙):
    import shutil
    source_dir, dest_dir = 甲, 乙
    for root, dirs, files in os.walk(source_dir):
        relative_path = os.path.relpath(root, source_dir)
        dest_root = os.path.join(dest_dir, relative_path)
        if not os.path.exists(dest_root):
            os.makedirs(dest_root, exist_ok=True)
        # 同步文件
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_root, file)
            if not os.path.exists(dest_file) or \
               (os.path.getmtime(src_file) > os.path.getmtime(dest_file)):
                try:
                    shutil.copy2(src_file, dest_file)
                except PermissionError as e:
                    logger.error(e)

    source_dir, dest_dir = dest_dir, source_dir
    for root, dirs, files in os.walk(source_dir):
        relative_path = os.path.relpath(root, source_dir)
        dest_root = os.path.join(dest_dir, relative_path)
        if not os.path.exists(dest_root):
            os.makedirs(dest_root, exist_ok=True)
        # 同步文件
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_root, file)
            if not os.path.exists(dest_file) or \
               (os.path.getmtime(src_file) > os.path.getmtime(dest_file)):
                try:
                    shutil.copy2(src_file, dest_file)
                except PermissionError as e:
                    logger.error(e)


def 同步檔案(目錄甲, 目錄乙, 檔):
    """同步单个文件，基于最后修改时间"""
    from datetime import datetime
    import shutil
    import os
    source, target, filename = 目錄甲, 目錄乙, 檔
    source_path = os.path.join(source, filename)
    target_path = os.path.join(target, filename)
    
    # 如果源文件不存在而目标文件存在
    if not os.path.exists(source_path) and os.path.exists(target_path):
        shutil.copy2(target_path, source_path)
        print(f"从目标复制到源: {filename}")
        return
    
    # 如果目标文件不存在而源文件存在
    if os.path.exists(source_path) and not os.path.exists(target_path):
        shutil.copy2(source_path, target_path)
        print(f"从源复制到目标: {filename}")
        return
    
    # 如果两边都存在文件
    if os.path.exists(source_path) and os.path.exists(target_path):
        source_mtime = os.path.getmtime(source_path)
        target_mtime = os.path.getmtime(target_path)
        
        if source_mtime > target_mtime:
            shutil.copy2(source_path, target_path)
            print(f"更新目标文件: {filename} (源文件较新)")
        elif target_mtime > source_mtime:
            shutil.copy2(target_path, source_path)
            print(f"更新源文件: {filename} (目标文件较新)")
        else:
            print(f"文件已同步: {filename}")
