"""
一键更新脚本 - Mihomo & ClashMetaForAndroid
自动下载最新版本并保存到下载文件夹
"""

import zipfile
from pathlib import Path
import requests
import shutil
import sys


def download_and_extract(repo_url, asset_filter, output_name, file_type):
    """
    下载并解压文件

    Args:
        repo_url: GitHub API URL
        asset_filter: 资源过滤条件函数
        output_name: 输出文件名
        file_type: 文件类型描述
    """
    download_dir = Path.home() / "Downloads"

    try:
        # 获取发布信息
        print(f"🔍 正在检查 {file_type} 最新版本...")
        response = requests.get(repo_url)
        response.raise_for_status()
        release = response.json()

        version = release["tag_name"]
        print(f"🎯 最新版本: {version}")

        # 查找匹配的资源
        asset = None
        for item in release["assets"]:
            if asset_filter(item.get("name", "")):
                asset = item
                break

        if not asset:
            print(f"❌ 未找到 {file_type} 版本")
            return False

        print(f"📦 找到资源: {asset['name']}")

        # 下载文件
        download_path = download_dir / asset["name"]
        print(f"⬇️  正在下载...")

        with requests.get(asset["browser_download_url"], stream=True) as response:
            response.raise_for_status()
            with open(download_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        final_path = download_dir / output_name

        # 处理文件
        if asset["name"].endswith(".zip"):
            # 解压压缩包
            temp_dir = download_dir / f"temp_{file_type.lower()}"
            temp_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(download_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # 查找目标文件
            target_file = None
            for file in temp_dir.iterdir():
                if file_type == "Mihomo" and file.suffix == ".exe":
                    target_file = file
                    break
                elif file_type == "ClashMetaForAndroid" and file.suffix == ".apk":
                    target_file = file
                    break

            if not target_file:
                print(f"❌ 在压缩包中未找到目标文件")
                shutil.rmtree(temp_dir, ignore_errors=True)
                download_path.unlink(missing_ok=True)
                return False

            # 移动最终文件
            shutil.move(str(target_file), str(final_path))

            # 清理临时文件
            shutil.rmtree(temp_dir, ignore_errors=True)
            download_path.unlink(missing_ok=True)
        else:
            # 直接重命名文件
            download_path.rename(final_path)

        print(f"✅ {file_type} 更新完成！文件位置: {final_path}")
        print(f"📋 版本号: {version}\n")
        return True

    except Exception as e:
        print(f"❌ {file_type} 更新出错: {e}\n")
        return False


def update_mihomo():
    """更新 Mihomo"""

    def mihomo_filter(name):
        return "windows-amd64-v3-go124" in name and name.endswith(".zip")

    return download_and_extract(
        repo_url="https://api.github.com/repos/MetaCubeX/mihomo/releases/latest",
        asset_filter=mihomo_filter,
        output_name="mihomo-windows-amd64.exe",
        file_type="Mihomo",
    )


def update_clash_android():
    """更新 ClashMetaForAndroid"""

    def clash_filter(name):
        name_lower = name.lower()
        return "arm64-v8a" in name_lower and (
            name_lower.endswith(".apk") or name_lower.endswith(".zip")
        )

    return download_and_extract(
        repo_url="https://api.github.com/repos/MetaCubeX/ClashMetaForAndroid/releases/latest",
        asset_filter=clash_filter,
        output_name="ClashMetaForAndroid.apk",
        file_type="ClashMetaForAndroid",
    )


def main():
    """主函数"""
    print("=" * 50)
    print("🚀 一键更新脚本 - Mihomo & ClashMetaForAndroid")
    print("=" * 50)

    # 更新 Mihomo
    mihomo_success = update_mihomo()

    # 更新 ClashMetaForAndroid
    clash_success = update_clash_android()

    # 显示结果摘要
    print("=" * 50)
    print("📊 更新结果摘要:")
    print(f"   Mihomo: {'✅ 成功' if mihomo_success else '❌ 失败'}")
    print(f"   ClashMetaForAndroid: {'✅ 成功' if clash_success else '❌ 失败'}")
    print("=" * 50)

    # 如果都失败则返回错误代码
    if not mihomo_success and not clash_success:
        sys.exit(1)


if __name__ == "__main__":
    main()
