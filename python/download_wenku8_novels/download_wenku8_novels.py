import sys
import requests
import html
import re


def clean_filename(filename):
    """
    清理文件名，移除不合法的字符

    Args:
        filename (str): 原始文件名

    Returns:
        str: 清理后的文件名
    """
    # 移除Windows不合法的字符
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "", filename)
    # 移除首尾空格
    cleaned = cleaned.strip()
    # 如果文件名为空，返回默认名称
    return cleaned if cleaned else "novel"


def download_and_process_novel(novel_id):
    """
    下载并处理wenku8小说

    Args:
        novel_id (str): 小说代码/ID
    """
    # 构建下载URL
    url = f"https://dl.wenku8.com/down.php?type=utf8&node=1&id={novel_id}"

    # 设置请求头以避免反爬虫
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.wenku8.com/",
    }

    try:
        # 下载小说文件
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 生成文件名
        filename = clean_filename(f"{novel_id}.txt")

        # 保存原始文件
        with open(filename, "wb") as f:
            f.write(response.content)

        print(f"小说已下载: {filename}")

        # 读取文件内容
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        # 转换HTML实体
        converted_content = html.unescape(content)

        # 写回文件
        with open(filename, "w", encoding="utf-8") as f:
            f.write(converted_content)

        print(f"小说处理完成: {filename}")

    except requests.RequestException as e:
        print(f"下载错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"处理错误: {e}")
        sys.exit(1)


def main():
    """主函数 - 处理命令行参数"""
    if len(sys.argv) != 2:
        print("用法: dwenku8 <小说代码>")
        print("示例: dwenku8 1234")
        sys.exit(1)

    # 获取小说ID并处理
    novel_id = sys.argv[1]
    download_and_process_novel(novel_id)


if __name__ == "__main__":
    main()
