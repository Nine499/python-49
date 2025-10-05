import uuid
import pyperclip


def generate_uuid():
    """
    生成UUIDv4并复制到剪贴板

    UUID (Universally Unique Identifier) 是一个128位的标识符，
    通常用于在分布式系统中唯一标识信息。
    UUIDv4是基于随机数生成的UUID。
    """
    # 生成UUIDv4
    uuid_value = uuid.uuid4()

    # 尝试复制到剪贴板，失败时提示手动复制
    try:
        pyperclip.copy(str(uuid_value))
        print(f"UUID已生成并复制到剪贴板: {uuid_value}")
    except Exception:
        print(f"UUID已生成 (请手动复制): {uuid_value}")


if __name__ == "__main__":
    generate_uuid()
