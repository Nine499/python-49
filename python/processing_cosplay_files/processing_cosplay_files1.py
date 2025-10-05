"""
Cosplay文件处理脚本1 - 优化版

优化说明：
1. 移除了不必要的线程锁，简化了并发处理
2. 合并了重复的异常处理代码
3. 使用更简洁的路径处理和文件操作
4. 改进了用户交互体验
5. 添加了更详细的注释，便于新手理解
"""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

# 常量定义（全大写表示常量）
FIXED_DIRECTORY = r"C:\Users\fortynine\acg\1"
SEVEN_ZIP_PATH = r"C:\Program Files\7-Zip\7z.exe"

# 支持的文件类型
ARCHIVE_EXTENSIONS = (".zip", ".rar", ".7z")
DELETE_EXTENSIONS = (".webp", ".gif")


def safe_delete(file_path):
    """
    安全删除文件，处理权限问题

    Args:
        file_path (str): 要删除的文件路径
    """
    try:
        os.remove(file_path)
        print(f"✓ 已删除: {os.path.basename(file_path)}")
    except PermissionError:
        # 如果是权限错误，修改权限后重试
        os.chmod(file_path, 0o666)  # 赋予读写权限
        os.remove(file_path)
        print(f"✓ 已删除(修复权限后): {os.path.basename(file_path)}")
    except Exception as e:
        print(f"✗ 删除失败 {os.path.basename(file_path)}: {e}")


def extract_single_archive(file_path, root_dir):
    """
    解压单个压缩文件

    Args:
        file_path (str): 压缩文件完整路径
        root_dir (str): 解压目标目录
    """
    try:
        print(f"正在解压: {os.path.basename(file_path)}")

        # 使用7z解压文件
        # 参数说明:
        # x: 解压并保持目录结构
        # -o: 指定输出目录
        # -y: 自动确认所有提示
        subprocess.run(
            [SEVEN_ZIP_PATH, "x", file_path, f"-o{root_dir}", "-y"],
            check=True,
            capture_output=True,
            text=True,
        )

        print(f"✓ 解压成功: {os.path.basename(file_path)}")

        # 解压成功后删除原文件
        safe_delete(file_path)
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ 解压失败 {os.path.basename(file_path)}: {e.stderr or e}")
        return False
    except Exception as e:
        print(f"✗ 处理失败 {os.path.basename(file_path)}: {e}")
        return False


def extract_archives(directory):
    """
    批量解压目录中的所有压缩文件

    Args:
        directory (str): 要处理的目录路径
    """
    if not os.path.exists(SEVEN_ZIP_PATH):
        print("错误: 未找到7-Zip程序，请检查安装路径")
        return

    # 收集所有压缩文件
    archive_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(ARCHIVE_EXTENSIONS):
                archive_files.append((os.path.join(root, file), root))

    if not archive_files:
        print("未找到压缩文件")
        return

    print(f"找到 {len(archive_files)} 个压缩文件，开始解压...")

    # 使用线程池并行处理
    # min(32, cpu_count + 4): 合理的线程数设置
    successful = 0
    with ThreadPoolExecutor(max_workers=min(32, (os.cpu_count() or 1) + 4)) as executor:
        # 提交所有解压任务
        futures = [
            executor.submit(extract_single_archive, file_path, root)
            for file_path, root in archive_files
        ]

        # 统计成功数量
        successful = sum(1 for future in futures if future.result())

    print(f"解压完成: 成功 {successful}/{len(archive_files)}")


def delete_unwanted_files(directory):
    """
    删除不需要的文件类型

    Args:
        directory (str): 要处理的目录路径
    """
    deleted_count = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(DELETE_EXTENSIONS):
                file_path = os.path.join(root, file)
                safe_delete(file_path)
                deleted_count += 1

    print(f"删除完成: 共删除 {deleted_count} 个文件")


def main():
    """
    主函数 - 程序入口点
    """
    # 检查目录是否存在
    if not os.path.exists(FIXED_DIRECTORY):
        print(f"错误: 目录不存在 - {FIXED_DIRECTORY}")
        sys.exit(1)

    # 用户确认
    print("=== Cosplay文件处理脚本 ===")
    print(f"目标目录: {FIXED_DIRECTORY}")
    print("即将执行:")
    print("1. 解压所有压缩文件 (ZIP/RAR/7Z)")
    print("2. 删除解压后的压缩文件")
    print("3. 删除 WEBP 和 GIF 文件")
    print("\n⚠️  警告: 此操作不可撤销!")

    # 更友好的确认方式
    confirmation = input("\n请输入 'YES' 确认执行: ").strip().upper()

    if confirmation != "YES":
        print("操作已取消")
        return

    # 执行处理流程
    print("\n开始处理...")
    extract_archives(FIXED_DIRECTORY)
    delete_unwanted_files(FIXED_DIRECTORY)
    print("\n✅ 所有操作完成!")


if __name__ == "__main__":
    main()
