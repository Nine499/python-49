"""
Mihomo 更新脚本

这个脚本用于从 GitHub 自动下载最新的 Mihomo Windows 版本，
解压并重命名为标准名称，方便用户使用。
"""

import os
import zipfile
from pathlib import Path
import requests
import shutil
import sys


def get_latest_mihomo_release():
    """
    获取最新 mihomo release 信息

    Returns:
        dict: 包含发布信息的字典，如果失败则返回 None
    """
    api_url = "https://api.github.com/repos/MetaCubeX/mihomo/releases/latest"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        release_data = response.json()
        return release_data
    except requests.RequestException as e:
        print(f"获取最新版本信息失败: {e}")
        return None


def find_windows_asset(assets):
    """
    从 assets 中找到 windows amd64 v3 go124 的 asset

    Args:
        assets (list): 发布资产列表

    Returns:
        dict: 包含匹配资产信息的字典，如果没有找到则返回 None
    """
    for asset in assets:
        name = asset.get("name", "")
        # 查找匹配的 windows amd64 v3 go124 zip 文件
        if "windows-amd64-v3-go124" in name and name.endswith(".zip"):
            return asset
    return None


def download_file(url, dest_path):
    """
    下载文件

    Args:
        url (str): 文件下载链接
        dest_path (Path): 保存文件的目标路径

    Returns:
        bool: 下载成功返回 True，否则返回 False
    """
    try:
        print(f"正在下载: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(dest_path, "wb") as file:
            # 使用 iter_content 分块下载，避免内存占用过高
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        print(f"下载完成: {dest_path}")
        return True
    except requests.RequestException as e:
        print(f"下载失败: {e}")
        return False


def extract_and_rename(zip_path, extract_to):
    """
    解压 zip 文件并重命名 exe 文件

    Args:
        zip_path (Path): ZIP 文件路径
        extract_to (Path): 解压目标目录

    Returns:
        bool: 解压和重命名成功返回 True，否则返回 False
    """
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)

        # 查找解压后的 exe 文件
        extracted_files = os.listdir(extract_to)
        exe_file = None
        for file in extracted_files:
            if file.endswith(".exe"):
                exe_file = file
                break

        if exe_file:
            old_exe_path = os.path.join(extract_to, exe_file)
            new_exe_path = os.path.join(extract_to, "mihomo-windows-amd64.exe")

            os.rename(old_exe_path, new_exe_path)
            print(f"已将 {exe_file} 重命名为 mihomo-windows-amd64.exe")
            return True
        else:
            print("在压缩包中未找到 exe 文件")
            return False
    except zipfile.BadZipFile:
        print("压缩文件损坏")
        return False
    except OSError as e:
        print(f"处理文件时出错: {e}")
        return False


def main():
    """
    主函数
    """
    # 获取 Windows 用户的下载文件夹路径
    download_dir = Path.home() / "Downloads"

    print("正在获取最新版本信息...")
    release_info = get_latest_mihomo_release()
    if not release_info:
        print("无法获取最新版本信息，程序退出")
        sys.exit(1)

    version = release_info.get("tag_name", "").lstrip("v")  # 获取版本号，去掉 'v' 前缀
    print(f"最新版本: {version}")

    assets = release_info.get("assets", [])
    target_asset = find_windows_asset(assets)

    if not target_asset:
        print("未找到匹配的 Windows amd64 v3 go124 资源文件")
        sys.exit(1)

    asset_name = target_asset["name"]
    asset_url = target_asset["browser_download_url"]
    print(f"找到匹配文件: {asset_name}")

    # 构建下载路径
    zip_save_path = download_dir / asset_name

    # 下载文件
    if not download_file(asset_url, zip_save_path):
        print("下载失败，程序退出")
        sys.exit(1)

    # 创建临时解压目录
    temp_extract_dir = download_dir / "temp_mihomo_extract"
    temp_extract_dir.mkdir(exist_ok=True)

    # 解压并重命名
    success = extract_and_rename(zip_save_path, temp_extract_dir)

    if success:
        final_exe_path = download_dir / "mihomo-windows-amd64.exe"
        temp_exe_path = temp_extract_dir / "mihomo-windows-amd64.exe"

        # 如果目标文件已存在，先删除
        if final_exe_path.exists():
            final_exe_path.unlink()

        # 将exe文件移动到下载目录
        shutil.move(str(temp_exe_path), str(final_exe_path))
        print(f"所有操作完成！mihomo-windows-amd64.exe 已保存到 {download_dir}")
    else:
        print("处理过程中出现错误")
        sys.exit(1)

    # 清理临时解压目录和下载的zip文件
    try:
        if temp_extract_dir.exists():
            shutil.rmtree(temp_extract_dir)
        if zip_save_path.exists():
            zip_save_path.unlink()
    except Exception as e:
        print(f"清理临时文件时出错: {e}")


# 程序入口点
if __name__ == "__main__":
    main()
