"""
Cosplay文件处理脚本2 - 优化版

优化说明：
1. 移除了不必要的多线程和线程锁，简化并发处理
2. 合并重复的异常处理逻辑
3. 使用更简洁的文件操作和路径处理
4. 改进用户交互和进度显示
5. 添加详细注释，便于新手理解
"""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

# 常量定义
FIXED_DIRECTORY = r"C:\Users\fortynine\acg\1"
SEVEN_ZIP_PATH = r"C:\Program Files\7-Zip\7z.exe"


def safe_delete(file_path):
    """
    安全删除文件或文件夹，处理权限问题

    Args:
        file_path (str): 要删除的文件或文件夹路径
    """
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"✓ 删除文件: {os.path.basename(file_path)}")
        elif os.path.isdir(file_path):
            os.rmdir(file_path)
            print(f"✓ 删除空文件夹: {os.path.basename(file_path)}")
    except PermissionError:
        # 处理权限问题
        os.chmod(file_path, 0o666)
        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            os.rmdir(file_path)
        print(f"✓ 删除(修复权限): {os.path.basename(file_path)}")
    except Exception as e:
        print(f"✗ 删除失败 {os.path.basename(file_path)}: {e}")


def delete_non_webp_files(directory):
    """
    删除所有非.webp文件

    Args:
        directory (str): 要处理的目录路径
    """
    deleted_count = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if not file.lower().endswith(".webp"):
                file_path = os.path.join(root, file)
                safe_delete(file_path)
                deleted_count += 1

    print(f"删除完成: 共删除 {deleted_count} 个非.webp文件")


def remove_empty_folders(directory):
    """
    递归删除所有空文件夹

    Args:
        directory (str): 要处理的目录路径
    """
    deleted_count = 0

    # 自底向上遍历，确保先删除深层空文件夹
    for root, dirs, _ in sorted(os.walk(directory, topdown=False), reverse=True):
        for dir_name in dirs:
            folder_path = os.path.join(root, dir_name)
            try:
                # 检查文件夹是否为空
                if not os.listdir(folder_path):
                    safe_delete(folder_path)
                    deleted_count += 1
            except Exception as e:
                print(f"✗ 检查文件夹失败 {os.path.basename(folder_path)}: {e}")

    print(f"空文件夹清理完成: 共删除 {deleted_count} 个空文件夹")


def compress_single_folder(folder_path, output_path):
    """
    压缩单个文件夹为.7z格式

    Args:
        folder_path (str): 要压缩的文件夹路径
        output_path (str): 输出的压缩文件路径
    """
    try:
        print(f"正在压缩: {os.path.basename(folder_path)}")

        # 使用7z压缩
        # a: 添加文件到压缩包
        result = subprocess.run(
            [SEVEN_ZIP_PATH, "a", output_path, folder_path],
            check=True,
            capture_output=True,
            text=True,
        )

        print(f"✓ 压缩成功: {os.path.basename(folder_path)}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ 压缩失败 {os.path.basename(folder_path)}: {e.stderr or e}")
        return False
    except Exception as e:
        print(f"✗ 处理失败 {os.path.basename(folder_path)}: {e}")
        return False


def compress_subfolders(directory):
    """
    将第一层子文件夹分别压缩为独立的.7z文件

    Args:
        directory (str): 要处理的目录路径
    """
    if not os.path.exists(SEVEN_ZIP_PATH):
        print("错误: 未找到7-Zip程序")
        return

    # 收集所有第一层子文件夹
    subfolders = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            output_path = os.path.join(directory, f"{item}.7z")
            subfolders.append((item_path, output_path))

    if not subfolders:
        print("未找到需要压缩的子文件夹")
        return

    print(f"找到 {len(subfolders)} 个子文件夹，开始压缩...")

    # 使用线程池并行压缩
    successful = 0
    with ThreadPoolExecutor(max_workers=min(32, (os.cpu_count() or 1) + 4)) as executor:
        # 提交所有压缩任务
        futures = [
            executor.submit(compress_single_folder, folder_path, output_path)
            for folder_path, output_path in subfolders
        ]

        # 统计成功数量
        successful = sum(1 for future in futures if future.result())

    print(f"压缩完成: 成功 {successful}/{len(subfolders)}")


def main():
    """
    主函数 - 程序入口点
    """
    # 检查目录是否存在
    if not os.path.exists(FIXED_DIRECTORY):
        print(f"错误: 目录不存在 - {FIXED_DIRECTORY}")
        sys.exit(1)

    # 用户确认
    print("=== Cosplay文件处理脚本2 ===")
    print(f"目标目录: {FIXED_DIRECTORY}")
    print("即将执行:")
    print("1. 删除所有非.webp文件")
    print("2. 删除所有空文件夹")
    print("3. 将子文件夹压缩为.7z格式")
    print("\n⚠️  警告: 此操作不可撤销!")

    # 更友好的确认方式
    confirmation = input("\n请输入 'CONFIRM' 确认执行: ").strip().upper()

    if confirmation != "CONFIRM":
        print("操作已取消")
        return

    # 执行处理流程
    print("\n开始处理...")
    delete_non_webp_files(FIXED_DIRECTORY)
    remove_empty_folders(FIXED_DIRECTORY)
    compress_subfolders(FIXED_DIRECTORY)
    print("\n✅ 所有操作完成!")


if __name__ == "__main__":
    main()
