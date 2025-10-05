import sys
import html


def convert_html_entities(input_file, output_file):
    """
    将HTML文件中的HTML实体转换为对应的字符

    例如: &amp; -> &, &lt; -> <, &gt; -> >, &quot; -> "

    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
    """
    try:
        # 读取输入文件内容
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 转换HTML实体
        converted_content = html.unescape(content)

        # 写入输出文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(converted_content)

        print(f"转换完成！输出文件: {output_file}")

    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")
    except Exception as e:
        print(f"错误: {e}")


def main():
    """主函数 - 处理命令行参数"""
    if len(sys.argv) != 3:
        print("用法: python convert_html_entities.py <输入文件> <输出文件>")
        print("示例: python convert_html_entities.py input.html output.html")
        sys.exit(1)

    # 直接传递命令行参数
    convert_html_entities(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
