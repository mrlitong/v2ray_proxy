#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V2Ray 综合管理工具
整合了自动安装、节点管理、订阅管理等所有功能

功能特性：
1. 完整的V2Ray安装和部署
2. 订阅管理（支持vmess/vless）
3. 节点切换和管理（支持订阅节点和内置节点）
4. 高级延迟测试
5. 系统代理配置
6. ProxyChains4同步
7. 配置备份和恢复
8. 详细的日志记录
9. 代理状态美化显示

作者：Claude Assistant
版本：2.1.0
"""

import os
import sys
import json
import base64
import subprocess
import time
import socket
import requests
import tempfile
import shutil
from urllib.parse import urlparse, unquote, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# 全局配置
CONFIG_DIR = "/etc/v2ray"
CONFIG_FILE = "/etc/v2ray/config.json"
SUBSCRIPTION_FILE = "/etc/v2ray/subscription.json"
LOG_FILE = "/var/log/v2ray_command.log"

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'

# 内置节点（来自v2ray_node_switcher.py）
BUILTIN_NODES = [
    # 香港节点
    {"name": "VIP-v2ray-Hong Kong 01", "server": "andromedae.weltknoten.xyz", "port": 30001, "region": "香港", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 02", "server": "monocerotis.weltknoten.xyz", "port": 30002, "region": "香港", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 03", "server": "orionis.weltknoten.xyz", "port": 30003, "region": "香港", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 04", "server": "phoenicis.weltknoten.xyz", "port": 30004, "region": "香港", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 05", "server": "scorpii.weltknoten.xyz", "port": 30020, "region": "香港", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 06", "server": "andromedae.weltknoten.xyz", "port": 30021, "region": "香港", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 07", "server": "monocerotis.weltknoten.xyz", "port": 30022, "region": "香港", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 08", "server": "orionis.weltknoten.xyz", "port": 30023, "region": "香港", "tls": "tls"},
    # 日本节点
    {"name": "VIP-v2ray-Japan 01", "server": "phoenicis.weltknoten.xyz", "port": 30005, "region": "日本", "tls": "tls"},
    {"name": "VIP-v2ray-Japan 02", "server": "scorpii.weltknoten.xyz", "port": 30006, "region": "日本", "tls": "tls"},
    # 韩国节点
    {"name": "VIP-v2ray-Korea", "server": "andromedae.weltknoten.xyz", "port": 30024, "region": "韩国", "tls": "tls"},
    # 新加坡节点
    {"name": "VIP-v2ray-Singapore 01", "server": "andromedae.weltknoten.xyz", "port": 30007, "region": "新加坡", "tls": "tls"},
    {"name": "VIP-v2ray-Singapore 02", "server": "monocerotis.weltknoten.xyz", "port": 30008, "region": "新加坡", "tls": "tls"},
    # 台湾节点
    {"name": "VIP-v2ray-Taiwan 01", "server": "orionis.weltknoten.xyz", "port": 30009, "region": "台湾", "tls": "tls"},
    {"name": "VIP-v2ray-Taiwan 02", "server": "orionis.weltknoten.xyz", "port": 30010, "region": "台湾", "tls": "tls"},
    # 美国节点
    {"name": "VIP-v2ray-United States 01", "server": "phoenicis.weltknoten.xyz", "port": 30011, "region": "美国", "tls": "tls"},
    {"name": "VIP-v2ray-United States 02", "server": "scorpii.weltknoten.xyz", "port": 30012, "region": "美国", "tls": "tls"},
    {"name": "VIP-v2ray-United States 03", "server": "andromedae.weltknoten.xyz", "port": 30013, "region": "美国", "tls": "tls"},
    {"name": "VIP-v2ray-United States 04", "server": "monocerotis.weltknoten.xyz", "port": 30014, "region": "美国", "tls": "tls"},
    # 其他地区
    {"name": "VIP-v2ray-Z-Canada", "server": "orionis.weltknoten.xyz", "port": 30018, "region": "加拿大", "tls": "tls"},
    {"name": "VIP-v2ray-Z-England", "server": "phoenicis.weltknoten.xyz", "port": 30015, "region": "英国", "tls": "tls"},
    {"name": "VIP-v2ray-Z-Germany", "server": "scorpii.weltknoten.xyz", "port": 30017, "region": "德国", "tls": "tls"},
    {"name": "VIP-v2ray-Z-India", "server": "andromedae.weltknoten.xyz", "port": 30016, "region": "印度", "tls": "tls"},
    {"name": "VIP-v2ray-Z-Russia", "server": "andromedae.weltknoten.xyz", "port": 30019, "region": "俄罗斯", "tls": "tls"},
]

# 默认UUID（来自v2ray_node_switcher.py）
DEFAULT_UUID = "39a279a5-55bb-3a27-ad9b-6ec81ff5779a"

def log(message, level="INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"
    
    # 写入日志文件
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_message + "\n")
    except:
        pass
    
    # 控制台输出
    if level == "ERROR":
        print(f"{Colors.RED}✗ {message}{Colors.END}")
    elif level == "SUCCESS":
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    elif level == "WARNING":
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
    else:
        print(f"  {message}")

def run_command(command, capture_output=True, check=True):
    """执行系统命令"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
            return result.stdout.strip()
        else:
            return subprocess.run(command, shell=True, check=check)
    except subprocess.CalledProcessError as e:
        log(f"命令执行失败: {command}\n错误: {e}", "ERROR")
        if check:
            raise
        return None

def check_system():
    """检查系统环境"""
    log("检查系统环境...", "INFO")
    
    # 检查操作系统
    if not os.path.exists("/etc/os-release"):
        log("不支持的操作系统", "ERROR")
        return False
    
    os_info = run_command("cat /etc/os-release | grep -E '^(ID|VERSION_ID)='")
    if "ubuntu" not in os_info.lower() and "debian" not in os_info.lower():
        log("警告：此脚本主要为 Ubuntu/Debian 设计，其他系统可能需要调整", "WARNING")
    
    # 检查权限
    if os.geteuid() != 0:
        log("需要 root 权限运行此脚本", "ERROR")
        log("请使用: sudo python3 " + sys.argv[0], "INFO")
        return False
    
    # 检查网络
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
    except:
        log("网络连接异常，请检查网络设置", "ERROR")
        return False
    
    return True

def install_dependencies():
    """安装依赖软件"""
    log("安装必要的依赖...", "INFO")
    
    dependencies = ["curl", "wget", "unzip", "jq", "proxychains4"]
    
    # 更新包列表
    run_command("apt-get update", capture_output=False)
    
    for dep in dependencies:
        if run_command(f"which {dep}", check=False):
            log(f"{dep} 已安装", "SUCCESS")
        else:
            log(f"安装 {dep}...", "INFO")
            run_command(f"apt-get install -y {dep}", capture_output=False)

def install_v2ray():
    """安装 V2Ray"""
    log("开始安装 V2Ray...", "INFO")
    
    # 检查是否已安装
    if os.path.exists("/usr/local/bin/v2ray"):
        v2ray_version = run_command("v2ray version | head -1", check=False)
        if v2ray_version:
            log(f"V2Ray 已安装: {v2ray_version}", "SUCCESS")
            return True
    
    # 下载安装脚本
    log("下载 V2Ray 安装脚本...", "INFO")
    install_script = "/tmp/install-release.sh"
    run_command(f"wget -O {install_script} https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh")
    run_command(f"chmod +x {install_script}")
    
    # 执行安装
    log("执行 V2Ray 安装...", "INFO")
    run_command(f"bash {install_script}", capture_output=False)
    
    # 创建配置目录
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # 清理
    os.remove(install_script)
    
    log("V2Ray 安装完成", "SUCCESS")
    return True

def parse_vmess(vmess_url):
    """解析 VMess 链接"""
    try:
        vmess_data = vmess_url.replace('vmess://', '')
        node_info = json.loads(base64.b64decode(vmess_data).decode('utf-8'))
        
        node = {
            "protocol": "vmess",
            "name": node_info.get("ps", "Unknown"),
            "server": node_info.get("add"),
            "port": int(node_info.get("port", 443)),
            "uuid": node_info.get("id"),
            "alterId": int(node_info.get("aid", 0)),
            "network": node_info.get("net", "tcp"),
            "tls": node_info.get("tls", ""),
            "sni": node_info.get("sni", node_info.get("add")),
            "type": node_info.get("type", "none"),
            "host": node_info.get("host", ""),
            "path": node_info.get("path", ""),
            "security": node_info.get("scy", "auto"),
            "alpn": node_info.get("alpn", ""),
            "original": vmess_url
        }
        
        # 推断地区
        node["region"] = infer_region(node["name"])
        return node
    except Exception as e:
        log(f"解析 VMess 节点失败: {str(e)}", "WARNING")
        return None

def parse_vless(vless_url):
    """解析 VLESS 链接"""
    try:
        parsed = urlparse(vless_url)
        params = parse_qs(parsed.query)
        
        node = {
            "protocol": "vless",
            "name": unquote(parsed.fragment) if parsed.fragment else "Unknown",
            "server": parsed.hostname,
            "port": parsed.port or 443,
            "uuid": parsed.username,
            "network": params.get("type", ["tcp"])[0],
            "tls": params.get("security", [""])[0],
            "sni": params.get("sni", [parsed.hostname])[0],
            "flow": params.get("flow", [""])[0],
            "host": params.get("host", [""])[0],
            "path": params.get("path", ["/"])[0],
            "alpn": params.get("alpn", [""])[0],
            "original": vless_url
        }
        
        # 推断地区
        node["region"] = infer_region(node["name"])
        return node
    except Exception as e:
        log(f"解析 VLESS 节点失败: {str(e)}", "WARNING")
        return None

def infer_region(name):
    """根据节点名称推断地区"""
    name_lower = name.lower()
    
    region_keywords = {
        "香港": ["hk", "hong kong", "香港", "hongkong"],
        "日本": ["jp", "japan", "日本", "tokyo"],
        "新加坡": ["sg", "singapore", "新加坡"],
        "美国": ["us", "america", "美国", "usa"],
        "韩国": ["kr", "korea", "韩国", "seoul"],
        "台湾": ["tw", "taiwan", "台湾"],
        "加拿大": ["ca", "canada", "加拿大"],
        "英国": ["uk", "britain", "英国", "london"],
        "德国": ["de", "germany", "德国", "frankfurt"],
        "印度": ["in", "india", "印度", "mumbai"],
        "俄罗斯": ["ru", "russia", "俄罗斯", "moscow"]
    }
    
    for region, keywords in region_keywords.items():
        if any(keyword in name_lower for keyword in keywords):
            return region
    
    return "其他"

def parse_subscription(url):
    """解析订阅内容"""
    log(f"获取订阅内容: {url}", "INFO")
    
    try:
        # 获取订阅内容
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        content = response.text.strip()
        
        # Base64 解码
        try:
            decoded = base64.b64decode(content).decode('utf-8')
        except:
            decoded = content
        
        # 解析节点
        nodes = []
        for line in decoded.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('vmess://'):
                node = parse_vmess(line)
                if node:
                    nodes.append(node)
            elif line.startswith('vless://'):
                node = parse_vless(line)
                if node:
                    nodes.append(node)
            elif line.startswith('ss://'):
                log(f"Shadowsocks链接暂不支持", "WARNING")
        
        log(f"成功解析 {len(nodes)} 个节点", "SUCCESS")
        return nodes
        
    except Exception as e:
        log(f"解析订阅失败: {str(e)}", "ERROR")
        return []

def generate_v2ray_config(node):
    """生成 V2Ray 配置"""
    config = {
        "log": {
            "loglevel": "warning"
        },
        "inbounds": [
            {
                "port": 10808,
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": True
                }
            },
            {
                "port": 10809,
                "protocol": "http",
                "settings": {}
            }
        ],
        "outbounds": [],
        "routing": {
            "rules": []
        }
    }
    
    # 根据协议生成出站配置
    if node.get("protocol") == "vmess":
        outbound = {
            "protocol": "vmess",
            "settings": {
                "vnext": [
                    {
                        "address": node["server"],
                        "port": node["port"],
                        "users": [
                            {
                                "id": node.get("uuid", DEFAULT_UUID),
                                "alterId": node.get("alterId", 0),
                                "security": node.get("security", "auto")
                            }
                        ]
                    }
                ]
            },
            "streamSettings": {
                "network": node.get("network", "tcp")
            }
        }
    elif node.get("protocol") == "vless":
        outbound = {
            "protocol": "vless",
            "settings": {
                "vnext": [
                    {
                        "address": node["server"],
                        "port": node["port"],
                        "users": [
                            {
                                "id": node.get("uuid", DEFAULT_UUID),
                                "encryption": "none",
                                "flow": node.get("flow", "")
                            }
                        ]
                    }
                ]
            },
            "streamSettings": {
                "network": node.get("network", "tcp")
            }
        }
    else:
        # 默认vmess配置（用于内置节点）
        outbound = {
            "protocol": "vmess",
            "settings": {
                "vnext": [
                    {
                        "address": node["server"],
                        "port": node["port"],
                        "users": [
                            {
                                "id": node.get("uuid", DEFAULT_UUID),
                                "alterId": 0,
                                "security": "auto"
                            }
                        ]
                    }
                ]
            },
            "streamSettings": {
                "network": "tcp"
            }
        }
    
    # TLS 配置
    if node.get("tls") in ["tls", "xtls"]:
        outbound["streamSettings"]["security"] = node.get("tls")
        outbound["streamSettings"]["tlsSettings"] = {
            "serverName": node.get("sni", node["server"]),
            "allowInsecure": False
        }
    
    # 网络配置
    if node.get("network") == "ws":
        outbound["streamSettings"]["wsSettings"] = {
            "path": node.get("path", "/"),
            "headers": {
                "Host": node.get("host", node["server"])
            }
        }
    
    config["outbounds"] = [outbound]
    return config

def test_node_latency(node, timeout=5, test_count=3):
    """测试节点延迟（高级版本）"""
    latencies = []
    
    for _ in range(test_count):
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((node["server"], node["port"]))
            sock.close()
            
            if result == 0:
                latency = (time.time() - start_time) * 1000
                latencies.append(latency)
            
            time.sleep(0.2)
        except:
            pass
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        return {
            "status": "在线",
            "latency": avg_latency,
            "success_rate": len(latencies) / test_count * 100
        }
    else:
        return {
            "status": "离线",
            "latency": 9999,
            "success_rate": 0
        }

def test_all_nodes(nodes):
    """批量测试所有节点"""
    print("\n正在测试所有节点，请稍候...")
    print("="*80)
    print(f"{'节点名称':<30} {'地区':<8} {'状态':<8} {'延迟(ms)':<12} {'成功率':<10}")
    print("="*80)
    
    results = []
    
    # 使用线程池并发测试
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_node = {executor.submit(test_node_latency, node): node for node in nodes}
        
        for future in as_completed(future_to_node):
            node = future_to_node[future]
            try:
                result = future.result()
                node_result = {**node, **result}
                results.append(node_result)
                
                # 实时显示结果
                if result["status"] == "在线":
                    status_str = f"{Colors.GREEN}在线{Colors.END}"
                    latency_str = f"{result['latency']:.1f}"
                    if result['latency'] < 100:
                        latency_str = f"{Colors.GREEN}{latency_str}{Colors.END}"
                    elif result['latency'] < 300:
                        latency_str = f"{Colors.YELLOW}{latency_str}{Colors.END}"
                    else:
                        latency_str = f"{Colors.RED}{latency_str}{Colors.END}"
                else:
                    status_str = f"{Colors.RED}离线{Colors.END}"
                    latency_str = "-"
                
                print(f"{node['name']:<30} {node.get('region', '未知'):<8} {status_str:<17} {latency_str:<20} {result['success_rate']:.0f}%")
                
            except Exception as e:
                print(f"{node['name']:<30} {node.get('region', '未知'):<8} {Colors.RED}错误{Colors.END}")
    
    print("="*80)
    
    # 统计信息
    online_nodes = [n for n in results if n["status"] == "在线"]
    if online_nodes:
        avg_latency = sum(n["latency"] for n in online_nodes) / len(online_nodes)
        best_node = min(online_nodes, key=lambda x: x["latency"])
        print(f"\n在线节点: {len(online_nodes)}/{len(nodes)}")
        print(f"平均延迟: {avg_latency:.1f}ms")
        print(f"\n{Colors.GREEN}推荐节点: {best_node['name']} (延迟: {best_node['latency']:.1f}ms){Colors.END}")
        return best_node
    else:
        print(f"\n{Colors.RED}所有节点都无法连接！{Colors.END}")
        return None

def configure_system_proxy():
    """配置系统代理"""
    log("配置系统代理...", "INFO")
    
    # 配置 ProxyChains4
    proxychains_config = "/etc/proxychains4.conf"
    if os.path.exists(proxychains_config):
        # 备份原配置
        shutil.copy(proxychains_config, f"{proxychains_config}.backup")
        
        # 修改配置
        with open(proxychains_config, 'r') as f:
            content = f.read()
        
        # 启用 dynamic_chain
        content = content.replace('strict_chain', '#strict_chain')
        content = content.replace('#dynamic_chain', 'dynamic_chain')
        
        # 设置代理
        if 'socks5  127.0.0.1 10808' not in content:
            # 替换旧端口
            content = content.replace('socks4 \t127.0.0.1 9050', 'socks5  127.0.0.1 10808')
            content = content.replace('socks5  127.0.0.1 1080', 'socks5  127.0.0.1 10808')
        
        with open(proxychains_config, 'w') as f:
            f.write(content)
        
        log("ProxyChains4 配置完成", "SUCCESS")
    
    # 配置 shell 环境变量
    shell_config = """
# V2Ray Proxy Configuration
export http_proxy="http://127.0.0.1:10809"
export https_proxy="http://127.0.0.1:10809"
export HTTP_PROXY="http://127.0.0.1:10809"
export HTTPS_PROXY="http://127.0.0.1:10809"
export socks_proxy="socks5://127.0.0.1:10808"
export all_proxy="socks5://127.0.0.1:10808"
export no_proxy="localhost,127.0.0.1,localaddress,.localdomain.com"

# Proxy control functions
proxy_on() {
    export http_proxy="http://127.0.0.1:10809"
    export https_proxy="http://127.0.0.1:10809"
    export HTTP_PROXY="http://127.0.0.1:10809"
    export HTTPS_PROXY="http://127.0.0.1:10809"
    export all_proxy="socks5://127.0.0.1:10808"
    echo "Proxy enabled"
}

proxy_off() {
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy
    echo "Proxy disabled"
}

proxy_status() {
    if [ -z "$http_proxy" ]; then
        echo "Proxy is OFF"
    else
        echo "Proxy is ON"
        echo "HTTP Proxy: $http_proxy"
        echo "SOCKS Proxy: $all_proxy"
    fi
}
"""
    
    # 写入配置文件
    proxy_sh = "/etc/profile.d/v2ray_proxy.sh"
    with open(proxy_sh, 'w') as f:
        f.write(shell_config)
    
    log("系统代理环境变量配置完成", "SUCCESS")
    log("新开终端将自动加载代理设置", "INFO")
    log("使用 proxy_on/proxy_off/proxy_status 控制代理", "INFO")

def save_subscription(url, nodes):
    """保存订阅信息"""
    subscription_data = {
        "url": url,
        "nodes": nodes,
        "update_time": int(time.time()),
        "selected_index": 0
    }
    
    # 备份现有配置
    if os.path.exists(SUBSCRIPTION_FILE):
        shutil.copy(SUBSCRIPTION_FILE, f"{SUBSCRIPTION_FILE}.backup")
    
    with open(SUBSCRIPTION_FILE, 'w', encoding='utf-8') as f:
        json.dump(subscription_data, f, indent=2, ensure_ascii=False)
    
    log("订阅信息已保存", "SUCCESS")

def load_subscription():
    """加载订阅信息"""
    try:
        if os.path.exists(SUBSCRIPTION_FILE):
            with open(SUBSCRIPTION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        log(f"加载订阅配置失败: {str(e)}", "ERROR")
        return None

def apply_node_config(node):
    """应用节点配置"""
    # 备份当前配置
    if os.path.exists(CONFIG_FILE):
        shutil.copy(CONFIG_FILE, f"{CONFIG_FILE}.backup")
    
    # 生成新配置
    config = generate_v2ray_config(node)
    
    # 保存配置
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # 验证配置
    result = run_command("/usr/local/bin/v2ray test -config " + CONFIG_FILE, check=False)
    if result and "Configuration OK" in result:
        log("配置验证通过", "SUCCESS")
    else:
        log("配置验证失败，恢复备份", "ERROR")
        shutil.copy(f"{CONFIG_FILE}.backup", CONFIG_FILE)
        return False
    
    # 重启服务
    run_command("systemctl daemon-reload")
    run_command("systemctl enable v2ray")
    run_command("systemctl restart v2ray")
    
    # 检查服务状态
    time.sleep(2)
    status = run_command("systemctl is-active v2ray", check=False)
    if status == "active":
        log(f"V2Ray 服务已启动，使用节点: {node['name']}", "SUCCESS")
        return True
    else:
        log("V2Ray 服务启动失败", "ERROR")
        return False

def test_proxy():
    """测试代理连接"""
    log("测试代理连接...", "INFO")
    
    test_urls = [
        ("SOCKS5", "curl -s -x socks5h://127.0.0.1:10808 https://ipinfo.io/ip -m 10"),
        ("HTTP", "curl -s -x http://127.0.0.1:10809 https://ipinfo.io/ip -m 10")
    ]
    
    for name, cmd in test_urls:
        ip = run_command(cmd, check=False)
        if ip and len(ip) < 20:
            log(f"{name} 代理测试成功，IP: {ip}", "SUCCESS")
        else:
            log(f"{name} 代理测试失败", "ERROR")

def get_current_ip():
    """获取当前IP信息"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-x", "socks5h://127.0.0.1:10808", "https://ipinfo.io", "--connect-timeout", "5"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            return f"{data.get('ip', 'Unknown')} ({data.get('city', '')}, {data.get('country', '')})"
        else:
            return "无法获取 IP 信息"
    except Exception as e:
        return f"错误: {str(e)}"

def get_current_node_info():
    """获取当前使用的节点信息"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        # 检查配置结构
        if ("outbounds" not in config or 
            not config["outbounds"] or 
            "settings" not in config["outbounds"][0] or
            "vnext" not in config["outbounds"][0]["settings"] or
            not config["outbounds"][0]["settings"]["vnext"]):
            return "配置格式错误"
            
        current_server = config["outbounds"][0]["settings"]["vnext"][0]["address"]
        current_port = config["outbounds"][0]["settings"]["vnext"][0]["port"]
        
        # 查找匹配的节点
        all_nodes = get_available_nodes()
        for node in all_nodes:
            if node["server"] == current_server and node["port"] == current_port:
                return f"{node['name']} ({node.get('region', '未知')})"
        
        return "未知节点"
    except:
        return "配置文件不存在或格式错误"

def get_available_nodes():
    """获取所有可用节点（订阅+内置）"""
    nodes = []
    
    # 加载订阅节点
    subscription = load_subscription()
    if subscription and subscription.get("nodes"):
        nodes.extend(subscription["nodes"])
    
    # 添加内置节点（如果没有订阅或需要备用）
    if not nodes:
        # 转换内置节点格式
        for node in BUILTIN_NODES:
            nodes.append({
                **node,
                "protocol": "vmess",
                "uuid": DEFAULT_UUID
            })
    
    return nodes

def quick_start():
    """快速开始（新用户向导）"""
    print(f"\n{Colors.HEADER}欢迎使用 V2Ray 快速配置向导{Colors.END}")
    print("="*60)
    
    # 检查系统
    if not check_system():
        return False
    
    # 安装依赖和V2Ray
    install_dependencies()
    install_v2ray()
    
    # 询问订阅方式
    print("\n请选择配置方式：")
    print("1. 使用订阅地址（推荐）")
    print("2. 使用内置节点")
    
    choice = input("\n请选择 [1-2]: ").strip()
    
    nodes = []
    if choice == "1":
        sub_url = input("\n请输入 V2Ray 订阅地址: ").strip()
        if sub_url:
            nodes = parse_subscription(sub_url)
            if nodes:
                save_subscription(sub_url, nodes)
    else:
        nodes = [{**node, "protocol": "vmess", "uuid": DEFAULT_UUID} for node in BUILTIN_NODES]
    
    if not nodes:
        log("未找到可用节点", "ERROR")
        return False
    
    # 测试并选择最佳节点
    best_node = test_all_nodes(nodes[:20])  # 只测试前20个
    if best_node:
        if apply_node_config(best_node):
            configure_system_proxy()
            test_proxy()
            log("\n✨ V2Ray 配置完成！", "SUCCESS")
            print(f"\n当前使用节点: {best_node['name']}")
            print(f"本地SOCKS5代理: 127.0.0.1:10808")
            print(f"本地HTTP代理: 127.0.0.1:10809")
            return True
    
    return False

def switch_node():
    """切换节点"""
    nodes = get_available_nodes()
    if not nodes:
        log("没有可用节点", "ERROR")
        return
    
    # 显示节点列表
    print("\n" + "="*60)
    print("可用节点列表")
    print("="*60)
    
    # 按地区分组
    regions = {}
    for i, node in enumerate(nodes):
        region = node.get("region", "其他")
        if region not in regions:
            regions[region] = []
        regions[region].append((i, node))
    
    for region, region_nodes in regions.items():
        print(f"\n【{region}】")
        for i, node in region_nodes:
            print(f"  {i+1:3d}. {node['name']:<30} {node['server']}:{node['port']}")
    
    print("\n" + "="*60)
    
    # 选择节点
    try:
        choice = input(f"\n请选择节点 [1-{len(nodes)}，0 返回]: ").strip()
        if choice == "0":
            return
        
        idx = int(choice) - 1
        if 0 <= idx < len(nodes):
            selected_node = nodes[idx]
            print(f"\n已选择: {selected_node['name']}")
            
            # 测试节点
            print("\n正在测试节点延迟...")
            test_result = test_node_latency(selected_node)
            if test_result["status"] == "在线":
                print(f"✓ 节点延迟: {test_result['latency']:.1f}ms")
            else:
                print("✗ 节点无法连接")
                confirm = input("\n节点可能不可用，是否继续切换? (y/n): ")
                if confirm.lower() != 'y':
                    return
            
            # 应用配置
            if apply_node_config(selected_node):
                print("\n正在验证连接...")
                ip_info = get_current_ip()
                print(f"当前 IP: {ip_info}")
    except ValueError:
        log("无效的输入", "ERROR")

def update_subscription():
    """更新订阅"""
    subscription = load_subscription()
    
    if not subscription:
        url = input("\n请输入订阅地址: ").strip()
        if not url:
            log("订阅地址不能为空", "ERROR")
            return
    else:
        url = subscription.get("url", "")
        update_time = subscription.get("update_time", 0)
        last_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(update_time))
        
        print(f"\n当前订阅地址: {url}")
        print(f"上次更新时间: {last_update}")
        
        choice = input("\n是否更新订阅? (y/n): ").strip().lower()
        if choice != 'y':
            return
    
    nodes = parse_subscription(url)
    if nodes:
        save_subscription(url, nodes)
        
        # 显示统计
        region_count = {}
        for node in nodes:
            region = node.get("region", "未知")
            region_count[region] = region_count.get(region, 0) + 1
        
        print("\n订阅更新成功！")
        for region, count in region_count.items():
            print(f"  {region}: {count} 个节点")

def restore_backup():
    """恢复配置备份"""
    backups = []
    
    # 检查可用备份
    if os.path.exists(f"{CONFIG_FILE}.backup"):
        backups.append(("V2Ray 配置", CONFIG_FILE, f"{CONFIG_FILE}.backup"))
    
    if os.path.exists(f"{SUBSCRIPTION_FILE}.backup"):
        backups.append(("订阅配置", SUBSCRIPTION_FILE, f"{SUBSCRIPTION_FILE}.backup"))
    
    if os.path.exists("/etc/proxychains4.conf.backup"):
        backups.append(("ProxyChains4 配置", "/etc/proxychains4.conf", "/etc/proxychains4.conf.backup"))
    
    if not backups:
        log("没有找到任何备份文件", "WARNING")
        return
    
    print("\n可用的备份：")
    for i, (name, _, _) in enumerate(backups, 1):
        print(f"{i}. {name}")
    
    try:
        choice = input(f"\n请选择要恢复的备份 [1-{len(backups)}，0 取消]: ").strip()
        if choice == "0":
            return
        
        idx = int(choice) - 1
        if 0 <= idx < len(backups):
            name, target, backup = backups[idx]
            shutil.copy(backup, target)
            log(f"{name}已恢复", "SUCCESS")
            
            if "V2Ray" in name:
                restart = input("\n是否重启 V2Ray 服务? (y/n): ")
                if restart.lower() == 'y':
                    run_command("systemctl restart v2ray")
    except ValueError:
        log("无效的输入", "ERROR")

def show_help():
    """显示帮助信息"""
    help_text = f"""
{Colors.HEADER}================================================================================
                        V2Ray 综合管理工具 - 使用帮助
================================================================================{Colors.END}

【功能特性】
  • 完整的 V2Ray 安装和部署流程
  • 支持订阅解析（vmess/vless协议）
  • 内置24个备用节点
  • 高级延迟测试（并发测试、成功率统计）
  • 系统代理配置（环境变量、ProxyChains4）
  • 配置备份和恢复功能
  • 详细的日志记录

【主要功能说明】

1. {Colors.BOLD}快速开始{Colors.END}
   - 适合新用户的一键配置向导
   - 自动安装 V2Ray 和依赖
   - 引导配置订阅或使用内置节点
   - 自动选择最佳节点

2. {Colors.BOLD}节点管理{Colors.END}
   - 切换节点：支持订阅节点和内置节点
   - 测试当前节点：检测连接状态和延迟
   - 测试所有节点：批量测试并推荐最佳节点

3. {Colors.BOLD}订阅管理{Colors.END}
   - 添加/更新订阅地址
   - 自动解析 vmess/vless 链接
   - 保存订阅信息供后续使用

4. {Colors.BOLD}系统配置{Colors.END}
   - 配置系统代理环境变量
   - 同步 ProxyChains4 配置
   - 提供 proxy_on/proxy_off 快捷命令

5. {Colors.BOLD}高级功能{Colors.END}
   - 查看服务状态和日志
   - 备份/恢复配置文件
   - 测试代理连接

【配置文件位置】
  - V2Ray 配置: /etc/v2ray/config.json
  - 订阅信息: /etc/v2ray/subscription.json
  - ProxyChains4: /etc/proxychains4.conf
  - 系统日志: /var/log/v2ray_command.log

【代理端口】
  - SOCKS5: 127.0.0.1:10808
  - HTTP: 127.0.0.1:10809

【使用技巧】
  - 首次使用请选择"快速开始"
  - 定期更新订阅获取最新节点
  - 使用批量测试找出最佳节点
  - 配置出错时可恢复备份

【命令行参数】
  - proxy_status : 显示当前代理状态信息（美化版）
  - --help, -h : 显示帮助信息
  
【待实现功能】
  - --install : 仅安装 V2Ray
  - --switch <n> : 快速切换到第n个节点
  - --test : 测试所有节点
  - --update : 更新订阅

================================================================================
"""
    print(help_text)

def show_status():
    """显示当前状态"""
    print(f"\n{Colors.HEADER}V2Ray 服务状态{Colors.END}")
    print("="*60)
    
    # 服务状态
    status = run_command("systemctl is-active v2ray", check=False)
    if status == "active":
        print(f"服务状态: {Colors.GREEN}运行中{Colors.END}")
    else:
        print(f"服务状态: {Colors.RED}已停止{Colors.END}")
    
    # 当前节点
    print(f"当前节点: {Colors.BOLD}{Colors.CYAN}{get_current_node_info()}{Colors.END}")
    
    # IP信息
    if status == "active":
        print("正在获取IP信息...")
        ip_info = get_current_ip()
        print(f"当前IP: {ip_info}")
    
    # 订阅信息
    subscription = load_subscription()
    if subscription:
        node_count = len(subscription.get("nodes", []))
        update_time = subscription.get("update_time", 0)
        last_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(update_time))
        print(f"\n订阅节点: {node_count} 个")
        print(f"上次更新: {last_update}")
    else:
        print("\n订阅节点: 未配置（使用内置节点）")
    
    print("="*60)

def get_proxy_ip_info():
    """获取代理IP详细信息"""
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "5", "-x", "socks5h://127.0.0.1:10808", "https://ipinfo.io"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        return None
    except:
        return None

def get_direct_ip_info():
    """获取直连IP详细信息"""
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "3", "--noproxy", "*", "https://ipinfo.io"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        return None
    except:
        return None

def get_current_node_detail():
    """获取当前节点详细信息"""
    try:
        if not os.path.exists(CONFIG_FILE):
            return None, None, None
        
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        # 获取协议和服务器信息
        outbound = config.get('outbounds', [{}])[0]
        protocol = outbound.get('protocol', 'unknown')
        
        if protocol in ['vmess', 'vless']:
            vnext = outbound.get('settings', {}).get('vnext', [{}])[0]
            server = vnext.get('address', 'unknown')
            port = vnext.get('port', 'unknown')
        else:
            return None, None, protocol
        
        # 查找节点名称
        node_name = None
        all_nodes = get_available_nodes()
        for node in all_nodes:
            if node["server"] == server and node["port"] == port:
                node_name = node['name']
                break
        
        return node_name, f"{server}:{port}", protocol
    except:
        return None, None, None

def show_proxy_status():
    """显示代理状态（美化版本）"""
    print()
    print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.CYAN}║                    🌐 V2Ray 代理状态信息                     ║{Colors.END}")
    print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.END}")
    
    # 获取V2Ray服务状态
    v2ray_status = run_command("systemctl is-active v2ray", check=False)
    if v2ray_status == "active":
        print(f"{Colors.GREEN}▸ V2Ray 服务状态: ✓ 运行中{Colors.END}")
    else:
        print(f"{Colors.RED}▸ V2Ray 服务状态: ✗ 已停止{Colors.END}")
    
    # 获取节点信息
    node_name, server_port, protocol = get_current_node_detail()
    
    if node_name:
        print(f"{Colors.BLUE}▸ 当前节点: {Colors.BOLD}{Colors.CYAN}🔸 {node_name} 🔸{Colors.END}")
        print(f"{Colors.BLUE}▸ 服务器: {Colors.END}{server_port} {Colors.PURPLE}[{protocol}]{Colors.END}")
    elif server_port:
        print(f"{Colors.BLUE}▸ 当前节点: {Colors.BOLD}{Colors.RED}未知节点{Colors.END}")
        print(f"{Colors.BLUE}▸ 服务器: {Colors.END}{server_port} {Colors.PURPLE}[{protocol}]{Colors.END}")
    else:
        print(f"{Colors.RED}▸ 节点状态: 未配置{Colors.END}")
    
    # 检查代理环境变量
    print()
    http_proxy = os.environ.get('http_proxy', '')
    https_proxy = os.environ.get('https_proxy', '')
    all_proxy = os.environ.get('all_proxy', '')
    
    if http_proxy or https_proxy or all_proxy:
        print(f"{Colors.GREEN}▸ 终端代理: ✓ 已配置{Colors.END}")
        if http_proxy:
            print(f"  {Colors.BLUE}HTTP:{Colors.END}  {http_proxy}")
        if https_proxy:
            print(f"  {Colors.BLUE}HTTPS:{Colors.END} {https_proxy}")
        if all_proxy:
            print(f"  {Colors.BLUE}SOCKS:{Colors.END} {all_proxy}")
    else:
        print(f"{Colors.YELLOW}▸ 终端代理: ⚠ 未配置{Colors.END}")
    
    # 获取IP信息
    print()
    print(f"{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")
    
    proxy_failed = False
    if v2ray_status == "active":
        print(f"{Colors.BLUE}▸ 正在检测网络连接...{Colors.END}")
        
        # 获取代理IP
        proxy_info = get_proxy_ip_info()
        if proxy_info:
            proxy_ip = proxy_info.get('ip', 'Unknown')
            proxy_country = proxy_info.get('country', '')
            proxy_city = proxy_info.get('city', '')
            proxy_org = proxy_info.get('org', '')
            
            print(f"{Colors.GREEN}▸ 代理IP: {Colors.YELLOW}{proxy_ip}{Colors.END} {Colors.BLUE}({proxy_country} {proxy_city}){Colors.END}")
            print(f"{Colors.GREEN}▸ ISP: {Colors.END}{proxy_org}")
        else:
            print(f"{Colors.RED}▸ 代理连接: ✗ 无法连接到代理服务器{Colors.END}")
            proxy_failed = True
        
        # 获取本地IP（用于对比）
        direct_info = get_direct_ip_info()
        if direct_info:
            direct_ip = direct_info.get('ip', 'Unknown')
            direct_country = direct_info.get('country', '')
            print(f"{Colors.BLUE}▸ 本地IP: {Colors.END}{direct_ip} {Colors.PURPLE}({direct_country}){Colors.END}")
    else:
        # V2Ray未运行，只显示本地IP
        direct_info = get_direct_ip_info()
        if direct_info:
            direct_ip = direct_info.get('ip', 'Unknown')
            direct_country = direct_info.get('country', '')
            direct_city = direct_info.get('city', '')
            print(f"{Colors.BLUE}▸ 当前IP: {Colors.END}{direct_ip} {Colors.PURPLE}({direct_country} {direct_city}){Colors.END}")
    
    print(f"{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")
    
    # 只在代理连接失败时显示快捷提示
    if proxy_failed:
        print()
        print(f"{Colors.PURPLE}💡 快捷命令:{Colors.END}")
        print(f"  {Colors.BLUE}▸{Colors.END} 切换节点: {Colors.YELLOW}python3 {sys.argv[0]}{Colors.END}")
        print(f"  {Colors.BLUE}▸{Colors.END} 查看状态: {Colors.YELLOW}sudo systemctl status v2ray{Colors.END}")
        print(f"  {Colors.BLUE}▸{Colors.END} 重启服务: {Colors.YELLOW}sudo systemctl restart v2ray{Colors.END}")
        print()
    else:
        print()

def show_main_menu():
    """显示主菜单"""
    print(f"\n{Colors.BOLD}V2Ray 综合管理工具 v2.1{Colors.END}")
    print("="*60)
    print(f"当前节点: {Colors.BOLD}{Colors.CYAN}{get_current_node_info()}{Colors.END}")
    print("="*60)
    print("1. 快速开始（推荐新用户）")
    print("2. 节点管理")
    print("   21. 切换节点")
    print("   22. 测试当前节点")
    print("   23. 测试所有节点")
    print("3. 订阅管理")
    print("   31. 更新订阅")
    print("4. 系统配置")
    print("   41. 配置系统代理")
    print("   42. 同步 ProxyChains4")
    print("5. 高级功能")
    print("   51. 查看服务状态")
    print("   52. 测试代理连接")
    print("   53. 恢复配置备份")
    print("   54. 查看日志")
    print("   55. 显示代理状态（美化版）")
    print("6. 帮助")
    print("0. 退出")
    print("="*60)

def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "proxy_status":
            # 直接显示代理状态并退出
            show_proxy_status()
            return 0
        elif sys.argv[1] in ["--help", "-h"]:
            print(f"使用方法: {sys.argv[0]} [选项]")
            print("\n选项:")
            print("  proxy_status    显示当前代理状态信息")
            print("  --help, -h      显示此帮助信息")
            print("\n无参数时进入交互式菜单")
            return 0
    
    # 进入交互式菜单
    print(f"{Colors.HEADER}V2Ray 综合管理工具{Colors.END}")
    print(f"版本: 2.1.0 | 适用: Ubuntu/Debian\n")
    
    while True:
        show_main_menu()
        choice = input("请选择操作: ").strip()
        
        try:
            if choice == "0":
                print("\n感谢使用！")
                break
            
            elif choice == "1":
                # 快速开始
                quick_start()
            
            elif choice == "21":
                # 切换节点
                switch_node()
            
            elif choice == "22":
                # 测试当前节点
                nodes = get_available_nodes()
                current_node = None
                
                # 查找当前节点
                try:
                    with open(CONFIG_FILE, 'r') as f:
                        config = json.load(f)
                    if config.get("outbounds"):
                        current_server = config["outbounds"][0]["settings"]["vnext"][0]["address"]
                        current_port = config["outbounds"][0]["settings"]["vnext"][0]["port"]
                        
                        for node in nodes:
                            if node["server"] == current_server and node["port"] == current_port:
                                current_node = node
                                break
                except:
                    pass
                
                if current_node:
                    print(f"\n当前节点: {current_node['name']}")
                    result = test_node_latency(current_node, test_count=5)
                    if result["status"] == "在线":
                        print(f"✓ 状态: {result['status']}")
                        print(f"✓ 延迟: {result['latency']:.1f}ms")
                        print(f"✓ 成功率: {result['success_rate']:.0f}%")
                    else:
                        print(f"✗ 节点离线")
                else:
                    log("无法识别当前节点", "ERROR")
            
            elif choice == "23":
                # 测试所有节点
                nodes = get_available_nodes()
                test_all_nodes(nodes)
            
            elif choice == "31":
                # 更新订阅
                update_subscription()
            
            elif choice == "41":
                # 配置系统代理
                configure_system_proxy()
            
            elif choice == "42":
                # 同步 ProxyChains4
                run_command("sudo sed -i 's/socks5  127.0.0.1 1080/socks5  127.0.0.1 10808/g' /etc/proxychains4.conf")
                log("ProxyChains4 配置已同步", "SUCCESS")
            
            elif choice == "51":
                # 查看服务状态
                show_status()
            
            elif choice == "52":
                # 测试代理
                test_proxy()
            
            elif choice == "53":
                # 恢复备份
                restore_backup()
            
            elif choice == "54":
                # 查看日志
                if os.path.exists(LOG_FILE):
                    run_command(f"tail -n 50 {LOG_FILE}", capture_output=False)
                else:
                    log("日志文件不存在", "WARNING")
            
            elif choice == "55":
                # 显示代理状态（美化版）
                show_proxy_status()
            
            elif choice == "6":
                # 帮助
                show_help()
            
            else:
                log("无效的选择", "WARNING")
            
            if choice != "0":
                input("\n按回车键继续...")
                
        except KeyboardInterrupt:
            print("\n\n操作已取消")
            break
        except Exception as e:
            log(f"发生错误: {str(e)}", "ERROR")
            input("\n按回车键继续...")

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        log(f"发生错误: {str(e)}", "ERROR")
        sys.exit(1)