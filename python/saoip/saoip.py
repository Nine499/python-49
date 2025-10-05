"""
SAO IP工具 - 优化版
功能：IP连通性测试和端口扫描
特点：代码简洁、新手友好、功能完整
"""

import sys
import socket
import ipaddress
import subprocess
import time
import platform
from concurrent.futures import ThreadPoolExecutor


def parse_ports(port_str):
    """解析端口字符串，支持逗号分隔和范围表示"""
    ports = []
    for part in port_str.split(","):
        if "-" in part:
            start, end = map(int, part.split("-"))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    return ports


def ping_ip(ip, timeout=1):
    """使用ICMP协议ping指定IP地址"""
    try:
        # 根据操作系统选择ping参数
        param = (
            ["-n", "1", "-w", str(timeout * 1000)]
            if platform.system() == "Windows"
            else ["-c", "1", "-W", str(timeout)]
        )
        cmd = ["ping"] + param + [str(ip)]

        start_time = time.time()
        # 执行ping命令并隐藏输出
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
            if platform.system() == "Windows"
            else 0,
        )
        response_time = (time.time() - start_time) * 1000

        return (True, response_time) if result.returncode == 0 else (False, None)
    except Exception:
        return False, None


def tcp_connect(ip, port, timeout=1):
    """使用TCP连接测试指定IP的端口"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        start_time = time.time()
        result = sock.connect_ex((str(ip), port))
        response_time = (time.time() - start_time) * 1000
        sock.close()

        return (True, response_time) if result == 0 else (False, None)
    except Exception:
        return False, None


def parse_ip_range(ip_str):
    """解析IP地址或CIDR格式的IP段"""
    try:
        network = ipaddress.ip_network(ip_str, strict=False)
        return list(network.hosts())
    except ValueError:
        try:
            return [ipaddress.ip_address(ip_str)]
        except ValueError:
            print(f"错误: 无效的IP地址格式 '{ip_str}'")
            return []


def scan_icmp(ips):
    """使用ICMP协议扫描IP地址列表"""
    print("ICMP扫描中...")
    print("-" * 40)

    def worker(ip):
        is_alive, response_time = ping_ip(ip)
        if is_alive:
            print(f"IP: {ip} 通 ({response_time:.2f} ms)")

    # 在Windows上降低并发数以避免句柄问题
    max_workers = 50 if platform.system() == "Windows" else 100
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(worker, ips)


def scan_tcp(ips, ports):
    """使用TCP协议扫描IP地址和端口组合"""
    print("TCP端口扫描中...")
    print("-" * 40)

    def worker(args):
        ip, port = args
        is_open, response_time = tcp_connect(ip, port)
        if is_open:
            print(f"IP: {ip}:{port} 开放 ({response_time:.2f} ms)")

    # 创建所有IP和端口的组合
    tasks = [(ip, port) for ip in ips for port in ports]
    # 在Windows上降低并发数以避免句柄问题
    max_workers = 50 if platform.system() == "Windows" else 100
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(worker, tasks)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  ICMP测试: python saoip.py <IP或IP段>")
        print("  TCP测试:  python saoip.py <IP或IP段> <端口列表>")
        print("\n示例:")
        print("  python saoip.py 192.168.1.1")
        print("  python saoip.py 192.168.1.1/24 80,443,81-8080")
        return

    # 解析IP地址
    ips = parse_ip_range(sys.argv[1])
    if not ips:
        return

    # 选择扫描模式
    if len(sys.argv) == 2:
        scan_icmp(ips)
    else:
        try:
            ports = parse_ports(sys.argv[2])
            scan_tcp(ips, ports)
        except ValueError:
            print(f"错误: 端口格式不正确 '{sys.argv[2]}'")


if __name__ == "__main__":
    main()
