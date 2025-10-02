import sys
import cloudscraper
import re
import requests
import html


def sanitize_filename(filename):
    """
    清洗文件名中的非法字符

    Windows系统中不允许在文件名中使用以下字符:
    \\ / : * ? " < > |
    此函数将这些非法字符替换为下划线，并限制文件名长度

    Args:
        filename (str): 原始文件名

    Returns:
        str: 清洗后的文件名
    """
    # 替换所有非法字符为下划线
    # 正则表达式 [\\/:*?"<>|] 匹配所有非法字符
    cleaned = re.sub(r'[\\/:*?"<>|]', "_", filename)
    # 去除首尾空格并限制长度为50个字符
    # strip()去除首尾空格，[:50]截取前50个字符
    cleaned = cleaned.strip()[:50]
    # 如果清洗后的文件名为空，则返回默认名称"default"
    return cleaned or "default"


def convert_html_entities_in_file(input_file_path, output_file_path):
    """
    将HTML文件中的HTML实体转换为对应的字符

    HTML实体是一些特殊字符的编码表示，例如:
    &amp;  ->  &
    &lt;   ->  <
    &gt;   ->  >
    &quot; ->  "

    Args:
        input_file_path (str): 输入文件的路径
        output_file_path (str): 输出文件的路径
    """
    # 尝试打开输入文件并读取内容
    try:
        # 使用utf-8编码打开文件，确保能正确处理中文等特殊字符
        with open(input_file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # 将HTML实体转换为对应的字符
        # html.unescape()函数可以将HTML实体转换为对应的字符
        converted_content = html.unescape(content)

        # 将转换后的内容写入输出文件
        with open(output_file_path, "w", encoding="utf-8") as file:
            file.write(converted_content)

        # 打印成功信息
        print(f"转换完成。结果已保存到 {output_file_path}")

    # 捕获文件未找到的异常
    except FileNotFoundError:
        print(f"错误: 未找到路径为 {input_file_path} 的文件。")
    # 捕获权限错误异常
    except PermissionError:
        print(f"错误: 没有权限访问文件 {input_file_path} 或 {output_file_path}。")
    # 捕获编码错误异常
    except UnicodeDecodeError:
        print(f"错误: 文件 {input_file_path} 编码格式不正确，无法读取。")
    # 捕获其他可能的异常
    except Exception as e:
        print(f"发生未知错误: {e}")


def download_file():
    """
    从wenku8网站下载小说文件

    该函数会从命令行参数或用户输入获取书籍ID，
    然后从网站下载对应的小说内容并保存为txt文件。
    """
    # 检查是否有命令行参数传入书籍ID
    if len(sys.argv) > 1:
        # 从命令行参数获取书籍ID
        book_id = sys.argv[1]
        print(f"正在处理书籍ID: {book_id}")
    else:
        # 如果没有命令行参数，则提示用户输入书籍ID
        book_id = input("请输入书籍ID数字: ")

    # 构造下载链接
    # type=utf8表示下载UTF-8编码的文本文件
    # node=1表示下载节点
    # id为书籍ID
    url = f"https://dl.wenku8.com/down.php?type=utf8&node=1&id={book_id}"

    try:
        # 创建cloudscraper实例来绕过Cloudflare防护
        scraper = cloudscraper.create_scraper()
        # 发送GET请求获取文件内容
        response = scraper.get(url)
        # 检查HTTP响应状态码，如果不是200会抛出异常
        response.raise_for_status()

        # 将响应内容按行分割
        lines = response.text.splitlines()

        # 检查文件内容是否足够多行以获取文件名
        if len(lines) >= 3:
            # 通常第三行(索引为2)包含文件名信息
            raw_name = lines[2].strip()
            # 清洗文件名并添加.txt扩展名
            clean_name = sanitize_filename(raw_name)
            filename = f"{clean_name}.txt"

            # 将内容写入文件
            with open(filename, "w", encoding="utf-8") as f:
                f.write(response.text)

            print(f"文件已成功保存为：{filename}")

            # 自动转换HTML实体
            converted_filename = f"{clean_name}_converted.txt"
            convert_html_entities_in_file(filename, converted_filename)
        else:
            print("错误: 文件内容不足三行，无法获取文件名")

    # 捕获网络相关异常
    except cloudscraper.exceptions.CloudflareChallengeError as e:
        print(f"Cloudflare验证错误: {str(e)}")
    except cloudscraper.exceptions.CloudflareCaptchaProvider as e:
        print(f"Cloudflare验证码错误: {str(e)}")
    # 捕获HTTP错误
    except requests.exceptions.HTTPError as e:
        print(f"HTTP错误: {str(e)}")
    # 捕获连接错误
    except requests.exceptions.ConnectionError as e:
        print(f"连接错误，请检查网络连接: {str(e)}")
    # 捕获超时错误
    except requests.exceptions.Timeout as e:
        print(f"请求超时: {str(e)}")
    # 捕获其他可能的异常
    except Exception as e:
        print(f"操作失败: {str(e)}")


# 程序入口点
if __name__ == "__main__":
    download_file()
