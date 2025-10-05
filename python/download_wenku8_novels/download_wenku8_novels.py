import requests
import html
import re
import sys
from bs4 import BeautifulSoup


def clean_filename(filename):
    """清洗文件名，移除非法字符"""
    return re.sub(r'[<>:"/\\|?*]', "", filename).strip()


def download_novel(novel_id):
    """下载小说并保存为文本文件"""

    # 设置请求头绕过Cloudflare
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # 获取小说标题
        title_url = f"https://www.wenku8.net/book/{novel_id}.htm"
        title_response = requests.get(title_url, headers=headers)
        title_response.raise_for_status()

        soup = BeautifulSoup(title_response.content, "html.parser")
        title = soup.title.string if soup.title else f"小说_{novel_id}"
        title = clean_filename(title)

        print(f"正在下载: {title}")

        # 下载小说内容
        download_url = f"https://dl.wenku8.com/down.php?type=utf8&node=1&id={novel_id}"
        content_response = requests.get(download_url, headers=headers)
        content_response.raise_for_status()
        content_response.encoding = "utf-8"

        # 完整HTML实体转换
        content = html.unescape(content_response.text)

        # 保存文件
        filename = f"{title}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"下载完成: {filename}")

    except requests.RequestException as e:
        print(f"下载失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python dwenku8.py <小说ID>")
        print("示例: python dwenku8.py 4879")
        sys.exit(1)

    novel_id = sys.argv[1]
    download_novel(novel_id)


if __name__ == "__main__":
    main()
