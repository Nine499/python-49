"""
版本更新脚本 - 优化版

优化方案：
1. 合并重复的目录遍历逻辑
2. 简化错误处理，统一使用try-except
3. 减少不必要的变量和中间步骤
4. 使用更清晰的函数命名和结构
5. 移除冗余的注释，保留核心说明
"""

import os
import sys
import shutil
from datetime import datetime
import toml
import subprocess


def find_folder_or_file(start_path, target_name, max_depth=3):
    """
    在指定目录中查找文件夹或文件

    Args:
        start_path: 开始搜索的目录
        target_name: 要查找的文件夹名或文件名
        max_depth: 最大搜索深度

    Returns:
        找到的路径或None
    """
    for root, dirs, files in os.walk(start_path):
        # 计算当前深度
        depth = root[len(start_path) :].count(os.sep)

        # 查找目标
        if target_name in dirs:
            return os.path.join(root, target_name)
        if target_name in files:
            return os.path.join(root, target_name)

        # 控制搜索深度
        if depth >= max_depth - 1:
            dirs.clear()

    return None


def update_version():
    """更新pyproject.toml中的版本号为时间戳格式"""
    # 查找pyproject.toml文件
    pyproject_path = find_folder_or_file(os.getcwd(), "pyproject.toml")
    if not pyproject_path:
        print("错误: 未找到pyproject.toml文件")
        return False

    try:
        # 读取并更新版本号
        with open(pyproject_path, "r", encoding="utf-8") as f:
            data = toml.load(f)

        old_version = data["project"]["version"]
        new_version = datetime.now().strftime("%Y.%m.%d.%H%M%S")

        data["project"]["version"] = new_version

        with open(pyproject_path, "w", encoding="utf-8") as f:
            toml.dump(data, f)

        print(f"版本号已更新: {old_version} -> {new_version}")
        return True

    except Exception as e:
        print(f"更新版本号失败: {e}")
        return False


def run_command(cmd, cwd=None):
    """
    运行命令行工具

    Args:
        cmd: 命令列表
        cwd: 工作目录

    Returns:
        执行成功返回True，否则False
    """
    try:
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, check=True
        )

        if result.stdout:
            print(f"输出: {result.stdout}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return False
    except FileNotFoundError:
        print("错误: 找不到命令，请确保工具已安装")
        return False


def clean_dist_folder():
    """清理dist文件夹"""
    dist_path = find_folder_or_file(os.getcwd(), "dist")
    if dist_path:
        try:
            shutil.rmtree(dist_path)
            print(f"已删除: {dist_path}")
        except Exception as e:
            print(f"删除dist文件夹失败: {e}")
            return False
    return True


def find_and_install_wheel():
    """查找并安装最新的whl文件"""
    # 查找所有whl文件
    wheel_files = []
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(".whl"):
                full_path = os.path.join(root, file)
                wheel_files.append((full_path, os.path.getmtime(full_path)))

    if not wheel_files:
        print("未找到whl文件")
        return False

    # 找到最新的whl文件
    latest_wheel = max(wheel_files, key=lambda x: x[1])[0]
    print(f"找到最新whl文件: {latest_wheel}")

    # 安装whl文件
    return run_command(["uv", "tool", "install", latest_wheel])


def main():
    """主流程"""
    print("=== 版本更新工具 ===\n")

    # 1. 清理dist文件夹
    print("1. 清理dist文件夹")
    if not clean_dist_folder():
        sys.exit(1)

    # 2. 更新版本号
    print("\n2. 更新版本号")
    if not update_version():
        sys.exit(1)

    # 3. 构建项目
    print("\n3. 构建项目")
    if not run_command(["uv", "build"]):
        sys.exit(1)

    # 4. 安装whl文件
    print("\n4. 安装whl文件")
    if not find_and_install_wheel():
        sys.exit(1)

    print("\n=== 所有步骤完成 ===")


if __name__ == "__main__":
    main()
