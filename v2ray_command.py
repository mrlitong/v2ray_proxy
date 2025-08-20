#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V2Ray Comprehensive Management Tool
Integrates automatic installation, node management, subscription management and all other functions

Features:
1. Complete V2Ray installation and deployment
2. Subscription management (supports vmess/vless)
3. Node switching and management (supports subscription nodes and built-in nodes)
4. Advanced latency testing
5. System proxy configuration
6. ProxyChains4 synchronization
7. Configuration backup and restore
8. Detailed logging
9. Beautified proxy status display

Author: Claude Assistant
Version: 2.1.0
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
import configparser
from urllib.parse import urlparse, unquote, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Global configuration
CONFIG_DIR = "/etc/v2ray"
CONFIG_FILE = "/etc/v2ray/config.json"
SUBSCRIPTION_FILE = "/etc/v2ray/subscription.json"
LOG_FILE = "/var/log/v2ray_command.log"

# Color output
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

# Built-in nodes (from v2ray_node_switcher.py)
BUILTIN_NODES = [
    # Hong Kong nodes
    {"name": "VIP-v2ray-Hong Kong 01", "server": "andromedae.weltknoten.xyz", "port": 30001, "region": "Hong Kong", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 02", "server": "monocerotis.weltknoten.xyz", "port": 30002, "region": "Hong Kong", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 03", "server": "orionis.weltknoten.xyz", "port": 30003, "region": "Hong Kong", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 04", "server": "phoenicis.weltknoten.xyz", "port": 30004, "region": "Hong Kong", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 05", "server": "scorpii.weltknoten.xyz", "port": 30020, "region": "Hong Kong", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 06", "server": "andromedae.weltknoten.xyz", "port": 30021, "region": "Hong Kong", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 07", "server": "monocerotis.weltknoten.xyz", "port": 30022, "region": "Hong Kong", "tls": "tls"},
    {"name": "VIP-v2ray-Hong Kong 08", "server": "orionis.weltknoten.xyz", "port": 30023, "region": "Hong Kong", "tls": "tls"},
    # Japan nodes
    {"name": "VIP-v2ray-Japan 01", "server": "phoenicis.weltknoten.xyz", "port": 30005, "region": "Japan", "tls": "tls"},
    {"name": "VIP-v2ray-Japan 02", "server": "scorpii.weltknoten.xyz", "port": 30006, "region": "Japan", "tls": "tls"},
    # Korea nodes
    {"name": "VIP-v2ray-Korea", "server": "andromedae.weltknoten.xyz", "port": 30024, "region": "Korea", "tls": "tls"},
    # Singapore nodes
    {"name": "VIP-v2ray-Singapore 01", "server": "andromedae.weltknoten.xyz", "port": 30007, "region": "Singapore", "tls": "tls"},
    {"name": "VIP-v2ray-Singapore 02", "server": "monocerotis.weltknoten.xyz", "port": 30008, "region": "Singapore", "tls": "tls"},
    # Taiwan nodes
    {"name": "VIP-v2ray-Taiwan 01", "server": "orionis.weltknoten.xyz", "port": 30009, "region": "Taiwan", "tls": "tls"},
    {"name": "VIP-v2ray-Taiwan 02", "server": "orionis.weltknoten.xyz", "port": 30010, "region": "Taiwan", "tls": "tls"},
    # USA nodes
    {"name": "VIP-v2ray-United States 01", "server": "phoenicis.weltknoten.xyz", "port": 30011, "region": "USA", "tls": "tls"},
    {"name": "VIP-v2ray-United States 02", "server": "scorpii.weltknoten.xyz", "port": 30012, "region": "USA", "tls": "tls"},
    {"name": "VIP-v2ray-United States 03", "server": "andromedae.weltknoten.xyz", "port": 30013, "region": "USA", "tls": "tls"},
    {"name": "VIP-v2ray-United States 04", "server": "monocerotis.weltknoten.xyz", "port": 30014, "region": "USA", "tls": "tls"},
    # Other regions
    {"name": "VIP-v2ray-Z-Canada", "server": "orionis.weltknoten.xyz", "port": 30018, "region": "Canada", "tls": "tls"},
    {"name": "VIP-v2ray-Z-England", "server": "phoenicis.weltknoten.xyz", "port": 30015, "region": "UK", "tls": "tls"},
    {"name": "VIP-v2ray-Z-Germany", "server": "scorpii.weltknoten.xyz", "port": 30017, "region": "Germany", "tls": "tls"},
    {"name": "VIP-v2ray-Z-India", "server": "andromedae.weltknoten.xyz", "port": 30016, "region": "India", "tls": "tls"},
    {"name": "VIP-v2ray-Z-Russia", "server": "andromedae.weltknoten.xyz", "port": 30019, "region": "Russia", "tls": "tls"},
]

# Default UUID (from v2ray_node_switcher.py)
DEFAULT_UUID = "39a279a5-55bb-3a27-ad9b-6ec81ff5779a"

def log(message, level="INFO"):
    """Log messages"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"

    # Write to log file
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_message + "\n")
    except:
        pass

    # Console output
    if level == "ERROR":
        print(f"{Colors.RED}✗ {message}{Colors.END}")
    elif level == "SUCCESS":
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    elif level == "WARNING":
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
    else:
        print(f"  {message}")

def run_command(command, capture_output=True, check=True):
    """Execute system command"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
            return result.stdout.strip()
        else:
            return subprocess.run(command, shell=True, check=check)
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {command}\nError: {e}", "ERROR")
        if check:
            raise
        return None

def check_system():
    """Check system environment"""
    log("Checking system environment...", "INFO")

    # Check operating system
    if not os.path.exists("/etc/os-release"):
        log("Unsupported operating system", "ERROR")
        return False

    os_info = run_command("cat /etc/os-release | grep -E '^(ID|VERSION_ID)='")
    if "ubuntu" not in os_info.lower() and "debian" not in os_info.lower():
        log("Warning: This script is primarily designed for Ubuntu/Debian, other systems may require adjustments", "WARNING")

    # Check permissions
    if os.geteuid() != 0:
        log("Root privileges required to run this script", "ERROR")
        log("Please use: sudo python3 " + sys.argv[0], "INFO")
        return False

    # Check network
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
    except:
        log("Network connection error, please check network settings", "ERROR")
        return False

    return True

def install_dependencies():
    """Install dependencies"""
    log("Installing necessary dependencies...", "INFO")

    dependencies = ["curl", "wget", "unzip", "jq", "proxychains4"]

    # Update package list
    run_command("apt-get update", capture_output=False)

    for dep in dependencies:
        if run_command(f"which {dep}", check=False):
            log(f"{dep} already installed", "SUCCESS")
        else:
            log(f"Installing {dep}...", "INFO")
            run_command(f"apt-get install -y {dep}", capture_output=False)

def fix_systemd_config_path():
    """Fix V2Ray systemd service config path to use standard path"""
    service_file = "/etc/systemd/system/v2ray.service"
    if not os.path.exists(service_file):
        service_file = "/lib/systemd/system/v2ray.service"
        if not os.path.exists(service_file):
            log("V2Ray service file not found", "WARNING")
            return

    try:
        # Read service file
        with open(service_file, 'r') as f:
            content = f.read()

        # Check if it's using non-standard config path
        if "/usr/local/etc/v2ray/config.json" in content:
            log("Fixing V2Ray service config path...", "INFO")
            # Replace with standard path
            content = content.replace("/usr/local/etc/v2ray/config.json", CONFIG_FILE)
            
            # Write back
            with open(service_file, 'w') as f:
                f.write(content)
            
            # Reload systemd
            run_command("systemctl daemon-reload")
            log("V2Ray service config path fixed", "SUCCESS")
    except Exception as e:
        log(f"Failed to fix service config path: {str(e)}", "WARNING")

def install_v2ray():
    """Install V2Ray"""
    log("Starting V2Ray installation...", "INFO")

    # Check if already installed
    if os.path.exists("/usr/local/bin/v2ray"):
        v2ray_version = run_command("v2ray version | head -1", check=False)
        if v2ray_version:
            log(f"V2Ray already installed: {v2ray_version}", "SUCCESS")
            return True

    # Check for local v2ray zip file
    local_zip = "v2ray-linux-64.zip"
    if os.path.exists(local_zip):
        log(f"Found local V2Ray archive: {local_zip}", "INFO")
        log("Using local file for installation...", "INFO")

        try:
            # Create directories
            run_command("mkdir -p /usr/local/bin")
            run_command("mkdir -p /usr/local/share/v2ray")
            run_command("mkdir -p /usr/local/etc/v2ray")
            run_command("mkdir -p /var/log/v2ray")

            # Extract zip file
            log("Extracting V2Ray files...", "INFO")
            run_command(f"unzip -o {local_zip} -d /tmp/v2ray-temp")

            # Copy binary files
            run_command("cp /tmp/v2ray-temp/v2ray /usr/local/bin/")
            run_command("chmod +x /usr/local/bin/v2ray")

            # Copy other files
            if os.path.exists("/tmp/v2ray-temp/geoip.dat"):
                run_command("cp /tmp/v2ray-temp/geoip.dat /usr/local/share/v2ray/")
            if os.path.exists("/tmp/v2ray-temp/geosite.dat"):
                run_command("cp /tmp/v2ray-temp/geosite.dat /usr/local/share/v2ray/")

            # Create systemd service file
            service_content = """[Unit]
Description=V2Ray Service
Documentation=https://www.v2fly.org/
After=network.target nss-lookup.target

[Service]
User=nobody
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ExecStart=/usr/local/bin/v2ray run -config /etc/v2ray/config.json
Restart=on-failure
RestartPreventExitStatus=23

[Install]
WantedBy=multi-user.target
"""
            with open("/etc/systemd/system/v2ray.service", "w") as f:
                f.write(service_content)

            # Reload systemd
            run_command("systemctl daemon-reload")

            # Cleanup
            run_command("rm -rf /tmp/v2ray-temp")

            log("V2Ray installed successfully from local file", "SUCCESS")

        except Exception as e:
            log(f"Local installation failed: {str(e)}", "ERROR")
            log("Falling back to online installation...", "INFO")
            # Continue with online installation below
        else:
            # Create configuration directory
            os.makedirs(CONFIG_DIR, exist_ok=True)
            # Fix systemd config path if needed
            fix_systemd_config_path()
            return True

    # Online installation (original method)
    log("Downloading V2Ray installation script...", "INFO")
    install_script = "/tmp/install-release.sh"
    run_command(f"wget -O {install_script} https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh")
    run_command(f"chmod +x {install_script}")

    # Execute installation
    log("Installing V2Ray...", "INFO")
    run_command(f"bash {install_script}", capture_output=False)

    # Create configuration directory
    os.makedirs(CONFIG_DIR, exist_ok=True)

    # Fix configuration path in systemd service file
    fix_systemd_config_path()

    # Cleanup
    os.remove(install_script)

    log("V2Ray installation completed", "SUCCESS")
    return True

def parse_vmess(vmess_url):
    """Parse VMess URL"""
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

        # Infer region
        node["region"] = infer_region(node["name"])
        return node
    except Exception as e:
        log(f"Failed to parse VMess node: {str(e)}", "WARNING")
        return None

def parse_vless(vless_url):
    """Parse VLESS URL"""
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

        # Infer region
        node["region"] = infer_region(node["name"])
        return node
    except Exception as e:
        log(f"Failed to parse VLESS node: {str(e)}", "WARNING")
        return None

def infer_region(name):
    """Infer region from node name"""
    name_lower = name.lower()

    region_keywords = {
        "Hong Kong": ["hk", "hong kong", "hongkong"],
        "Japan": ["jp", "japan", "tokyo"],
        "Singapore": ["sg", "singapore"],
        "USA": ["us", "america", "usa"],
        "Korea": ["kr", "korea", "seoul"],
        "Taiwan": ["tw", "taiwan"],
        "Canada": ["ca", "canada"],
        "UK": ["uk", "britain", "london"],
        "Germany": ["de", "germany", "frankfurt"],
        "India": ["in", "india", "mumbai"],
        "Russia": ["ru", "russia", "moscow"]
    }

    for region, keywords in region_keywords.items():
        if any(keyword in name_lower for keyword in keywords):
            return region

    return "Other"

def parse_subscription(url):
    """Parse subscription content"""
    log(f"Fetching subscription content: {url}", "INFO")

    try:
        # Get subscription content
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        content = response.text.strip()

        # Base64 decode
        try:
            decoded = base64.b64decode(content).decode('utf-8')
        except:
            decoded = content

        # Parse nodes
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
                log(f"Shadowsocks links not yet supported", "WARNING")

        log(f"Successfully parsed {len(nodes)} nodes", "SUCCESS")
        return nodes

    except Exception as e:
        log(f"Failed to parse subscription: {str(e)}", "ERROR")
        return []

def generate_v2ray_config(node):
    """Generate V2Ray configuration"""
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

    # Generate outbound configuration based on protocol
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
        # Default vmess configuration (for built-in nodes)
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

    # TLS configuration
    if node.get("tls") in ["tls", "xtls"]:
        outbound["streamSettings"]["security"] = node.get("tls")
        outbound["streamSettings"]["tlsSettings"] = {
            "serverName": node.get("sni", node["server"]),
            "allowInsecure": False
        }

    # Network configuration
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
    """Test node latency (advanced version)"""
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
            "status": "online",
            "latency": avg_latency,
            "success_rate": len(latencies) / test_count * 100
        }
    else:
        return {
            "status": "offline",
            "latency": 9999,
            "success_rate": 0
        }

def test_all_nodes(nodes):
    """Batch test all nodes"""
    print("\nTesting all nodes, please wait...")
    
    # Filter out non-node entries (like subscription metadata)
    def is_valid_node(node):
        """Check if this is a valid VPN node"""
        node_name = node.get('name', '').lower()
        # Filter out subscription metadata entries
        if any(keyword in node_name for keyword in ['剩余流量', '过期时间', 'traffic', 'expire', 'remaining']):
            return False
        # Check if node has required fields
        if not node.get('server') or not node.get('port'):
            return False
        return True
    
    # Filter nodes
    valid_nodes = [node for node in nodes if is_valid_node(node)]
    
    if not valid_nodes:
        print(f"{Colors.RED}No valid nodes to test!{Colors.END}")
        return None

    # Calculate string display width in terminal (Chinese characters take 2 widths)
    def get_display_width(s):
        """Calculate string display width in terminal"""
        width = 0
        for char in s:
            if '\u4e00' <= char <= '\u9fff':  # Chinese character range
                width += 2
            else:
                width += 1
        return width

    # Format string to specified width
    def pad_to_width(text, target_width):
        """Pad text to specified display width"""
        current_width = get_display_width(text)
        padding_needed = target_width - current_width
        if padding_needed > 0:
            return text + ' ' * padding_needed
        return text

    # Define column widths
    NAME_WIDTH = 35
    REGION_WIDTH = 10  # Enough for "Russia" (6 display width) + some space
    STATUS_WIDTH = 10
    LATENCY_WIDTH = 15
    RATE_WIDTH = 10

    # Print header
    print("="*85)
    header = (
        f"{pad_to_width('Node Name', NAME_WIDTH)}"
        f"{pad_to_width('Region', REGION_WIDTH)}"
        f"{pad_to_width('Status', STATUS_WIDTH)}"
        f"{pad_to_width('Latency(ms)', LATENCY_WIDTH)}"
        f"Success Rate"
    )
    print(header)
    print("="*85)

    results = []

    # Use thread pool for concurrent testing
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_node = {executor.submit(test_node_latency, node): node for node in valid_nodes}

        for future in as_completed(future_to_node):
            node = future_to_node[future]
            try:
                result = future.result()
                node_result = {**node, **result}
                results.append(node_result)

                # Prepare column data
                name = node['name']
                region = node.get('region', 'Unknown')

                # Display results in real-time
                if result["status"] == "online":
                    latency_val = f"{result['latency']:.1f}"
                    if result['latency'] <= 80:
                        latency_colored = f"{Colors.GREEN}{latency_val}{Colors.END}"
                    elif result['latency'] <= 150:
                        latency_colored = f"{Colors.YELLOW}{latency_val}{Colors.END}"
                    else:
                        latency_colored = f"{Colors.RED}{latency_val}{Colors.END}"

                    # Format success rate with color
                    success_rate = result['success_rate']
                    success_rate_val = f"{success_rate:.0f}%"
                    if success_rate >= 90:
                        success_rate_colored = f"{Colors.GREEN}{success_rate_val}{Colors.END}"
                    elif success_rate >= 80:
                        success_rate_colored = f"{Colors.YELLOW}{success_rate_val}{Colors.END}"
                    else:
                        success_rate_colored = f"{Colors.RED}{success_rate_val}{Colors.END}"

                    # Build output line
                    line = (
                        f"{pad_to_width(name, NAME_WIDTH)}"
                        f"{pad_to_width(region, REGION_WIDTH)}"
                        f"{Colors.GREEN}Online{Colors.END}{' ' * (STATUS_WIDTH - get_display_width('Online'))}"
                        f"{latency_colored}{' ' * (LATENCY_WIDTH - get_display_width(latency_val))}"
                        f"{success_rate_colored}"
                    )
                else:
                    # Offline status
                    success_rate = result['success_rate']
                    success_rate_val = f"{success_rate:.0f}%"
                    # Offline nodes always show red success rate
                    success_rate_colored = f"{Colors.RED}{success_rate_val}{Colors.END}"

                    line = (
                        f"{pad_to_width(name, NAME_WIDTH)}"
                        f"{pad_to_width(region, REGION_WIDTH)}"
                        f"{Colors.RED}Offline{Colors.END}{' ' * (STATUS_WIDTH - get_display_width('Offline'))}"
                        f"-{' ' * (LATENCY_WIDTH - 1)}"
                        f"{success_rate_colored}"
                    )

                print(line)

            except Exception as e:
                # Error handling
                line = (
                    f"{pad_to_width(node['name'], NAME_WIDTH)}"
                    f"{pad_to_width(node.get('region', 'Unknown'), REGION_WIDTH)}"
                    f"{Colors.RED}Error{Colors.END}"
                )
                print(line)

    print("="*85)

    # Statistics
    online_nodes = [n for n in results if n["status"] == "online"]
    if online_nodes:
        avg_latency = sum(n["latency"] for n in online_nodes) / len(online_nodes)
        best_node = min(online_nodes, key=lambda x: x["latency"])
        print(f"\nOnline nodes: {len(online_nodes)}/{len(valid_nodes)}")
        print(f"Average latency: {avg_latency:.1f}ms")
        print(f"\n{Colors.GREEN}Recommended node: {best_node['name']} (Latency: {best_node['latency']:.1f}ms){Colors.END}")
        return best_node
    else:
        print(f"\n{Colors.RED}All nodes are unreachable!{Colors.END}")
        return None

def configure_system_proxy():
    """Configure system proxy"""
    log("Configuring system proxy...", "INFO")

    # Configure ProxyChains4
    proxychains_config = "/etc/proxychains4.conf"
    if os.path.exists(proxychains_config):
        # Backup original configuration
        shutil.copy(proxychains_config, f"{proxychains_config}.backup")

        # Modify configuration
        with open(proxychains_config, 'r') as f:
            content = f.read()

        # Enable dynamic_chain
        content = content.replace('strict_chain', '#strict_chain')
        content = content.replace('#dynamic_chain', 'dynamic_chain')

        # Set proxy
        if 'socks5  127.0.0.1 10808' not in content:
            # Replace old port
            content = content.replace('socks4 \t127.0.0.1 9050', 'socks5  127.0.0.1 10808')
            content = content.replace('socks5  127.0.0.1 1080', 'socks5  127.0.0.1 10808')

        with open(proxychains_config, 'w') as f:
            f.write(content)

        log("ProxyChains4 configuration completed", "SUCCESS")

    # Configure shell environment variables
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

    # Write configuration file for bash
    proxy_sh = "/etc/profile.d/v2ray_proxy.sh"
    with open(proxy_sh, 'w') as f:
        f.write(shell_config)

    # Check user's shell and configure accordingly
    user_shell = os.environ.get('SHELL', '/bin/bash')
    
    # Get the actual user's home directory (even if running with sudo)
    actual_user = os.environ.get('SUDO_USER', os.environ.get('USER'))
    if actual_user:
        import pwd
        user_info = pwd.getpwnam(actual_user)
        actual_home = user_info.pw_dir
        actual_uid = user_info.pw_uid
        actual_gid = user_info.pw_gid
    else:
        actual_home = os.path.expanduser('~')
        actual_uid = os.getuid()
        actual_gid = os.getgid()
    
    if 'zsh' in user_shell:
        # For zsh users, also add to .zshrc
        zshrc_path = os.path.join(actual_home, '.zshrc')
        
        # Check if the source line already exists
        source_line = 'source /etc/profile.d/v2ray_proxy.sh'
        
        try:
            with open(zshrc_path, 'r') as f:
                zshrc_content = f.read()
                
            if source_line not in zshrc_content:
                # Add source command to .zshrc
                with open(zshrc_path, 'a') as f:
                    f.write(f'\n# V2Ray Proxy Configuration\n{source_line}\n')
                # Set proper ownership
                os.chown(zshrc_path, actual_uid, actual_gid)
                log("Added proxy configuration to ~/.zshrc", "SUCCESS")
            else:
                log("Proxy configuration already exists in ~/.zshrc", "INFO")
        except FileNotFoundError:
            # Create .zshrc if it doesn't exist
            with open(zshrc_path, 'w') as f:
                f.write(f'# V2Ray Proxy Configuration\n{source_line}\n')
            # Set proper ownership
            os.chown(zshrc_path, actual_uid, actual_gid)
            log("Created ~/.zshrc with proxy configuration", "SUCCESS")
    
    log("System proxy environment variables configured", "SUCCESS")
    log("New terminals will automatically load proxy settings", "INFO")
    log("Use proxy_on/proxy_off/proxy_status to control proxy", "INFO")
    
    if 'zsh' in user_shell:
        log("For current session, run: source ~/.zshrc", "INFO")

def save_subscription(url, nodes):
    """Save subscription information"""
    subscription_data = {
        "url": url,
        "nodes": nodes,
        "update_time": int(time.time()),
        "selected_index": 0
    }

    # Backup existing configuration
    if os.path.exists(SUBSCRIPTION_FILE):
        shutil.copy(SUBSCRIPTION_FILE, f"{SUBSCRIPTION_FILE}.backup")

    with open(SUBSCRIPTION_FILE, 'w', encoding='utf-8') as f:
        json.dump(subscription_data, f, indent=2, ensure_ascii=False)

    log("Subscription information saved", "SUCCESS")

def load_subscription():
    """Load subscription information"""
    try:
        if os.path.exists(SUBSCRIPTION_FILE):
            with open(SUBSCRIPTION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        log(f"Failed to load subscription configuration: {str(e)}", "ERROR")
        return None

def apply_node_config(node):
    """Apply node configuration"""
    # Both possible config file locations
    config_locations = [
        CONFIG_FILE,  # /etc/v2ray/config.json
        "/usr/local/etc/v2ray/config.json"
    ]

    # Generate new configuration
    config = generate_v2ray_config(node)

    # Save configuration to all possible locations
    for config_path in config_locations:
        try:
            # Backup current configuration if exists
            if os.path.exists(config_path):
                shutil.copy(config_path, f"{config_path}.backup")

            # Create directory if not exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            # Save configuration
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            log(f"Configuration saved to: {config_path}", "INFO")
        except Exception as e:
            log(f"Failed to save config to {config_path}: {str(e)}", "WARNING")

    # Verify configuration
    result = run_command("/usr/local/bin/v2ray test -config " + CONFIG_FILE, check=False)
    if result and "Configuration OK" in result:
        log("Configuration validation passed", "SUCCESS")
    else:
        log("Configuration validation failed, restoring backup", "ERROR")
        for config_path in config_locations:
            if os.path.exists(f"{config_path}.backup"):
                shutil.copy(f"{config_path}.backup", config_path)
        return False

    # Restart service
    run_command("systemctl daemon-reload")
    run_command("systemctl enable v2ray")
    run_command("systemctl restart v2ray")

    # Check service status
    time.sleep(2)
    status = run_command("systemctl is-active v2ray", check=False)
    if status == "active":
        log(f"V2Ray service started, using node: {node['name']}", "SUCCESS")
        return True
    else:
        log("V2Ray service failed to start", "ERROR")
        return False

def test_proxy():
    """Test proxy connection"""
    log("Testing proxy connection...", "INFO")

    test_urls = [
        ("SOCKS5", "curl -s -x socks5h://127.0.0.1:10808 https://ipinfo.io/ip -m 10"),
        ("HTTP", "curl -s -x http://127.0.0.1:10809 https://ipinfo.io/ip -m 10")
    ]

    for name, cmd in test_urls:
        ip = run_command(cmd, check=False)
        if ip and len(ip) < 20:
            log(f"{name} proxy test successful, IP: {ip}", "SUCCESS")
        else:
            log(f"{name} proxy test failed", "ERROR")

def get_current_ip():
    """Get current IP information"""
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
            return "Unable to get IP info"
    except Exception as e:
        return f"Error: {str(e)}"

def get_current_node_info():
    """Get current node information"""
    # Check multiple possible config locations
    config_locations = [
        CONFIG_FILE,  # /etc/v2ray/config.json
        "/usr/local/etc/v2ray/config.json"
    ]

    config = None
    for config_path in config_locations:
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    break
        except:
            continue

    if not config:
        return "Configuration file not found"

    try:
        # Check configuration structure
        if ("outbounds" not in config or
            not config["outbounds"] or
            "settings" not in config["outbounds"][0] or
            "vnext" not in config["outbounds"][0]["settings"] or
            not config["outbounds"][0]["settings"]["vnext"]):
            return "Invalid configuration format"

        current_server = config["outbounds"][0]["settings"]["vnext"][0]["address"]
        current_port = config["outbounds"][0]["settings"]["vnext"][0]["port"]

        # Find matching node
        all_nodes = get_available_nodes()
        for node in all_nodes:
            if node["server"] == current_server and node["port"] == current_port:
                return f"{node['name']} ({node.get('region', 'Unknown')})"

        return "Unknown Node"
    except:
        return "Configuration file not found or invalid format"

def get_available_nodes():
    """Get all available nodes (subscription + built-in)"""
    nodes = []

    # Load subscription nodes
    subscription = load_subscription()
    if subscription and subscription.get("nodes"):
        nodes.extend(subscription["nodes"])

    # Add built-in nodes (if no subscription or need backup)
    if not nodes:
        # Convert built-in node format
        for node in BUILTIN_NODES:
            nodes.append({
                **node,
                "protocol": "vmess",
                "uuid": DEFAULT_UUID
            })

    return nodes

def get_default_subscription_url():
    """Get default subscription URL from subscription_url.ini"""
    ini_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "subscription_url.ini")
    
    if not os.path.exists(ini_path):
        return None
    
    try:
        config = configparser.ConfigParser()
        config.read(ini_path, encoding='utf-8')
        
        # Check for v2ray URL in gsou_cloud section
        if config.has_section('gsou_cloud') and config.has_option('gsou_cloud', 'v2ray'):
            return config.get('gsou_cloud', 'v2ray')
            
        # If not found in expected section, try to find any v2ray URL
        for section in config.sections():
            if config.has_option(section, 'v2ray'):
                return config.get(section, 'v2ray')
                
    except Exception as e:
        log(f"Failed to read default subscription URL: {str(e)}", "WARNING")
    
    return None

def quick_start():
    """Quick start (new user guide)"""
    print(f"\n{Colors.HEADER}Welcome to V2Ray Quick Setup Wizard{Colors.END}")
    print("="*60)

    # Check system
    if not check_system():
        return False

    # Install dependencies and V2Ray
    install_dependencies()
    install_v2ray()

    # Ask for subscription method
    print("\nPlease select configuration method:")
    print("1. Use subscription URL (recommended)")
    print("2. Use built-in nodes")

    choice = input("\nPlease select [1-2]: ").strip()

    nodes = []
    if choice == "1":
        # Get default subscription URL
        default_url = get_default_subscription_url()
        
        if default_url:
            print(f"\nFound default subscription URL:")
            print(f"{Colors.CYAN}{default_url}{Colors.END}")
            use_default = input("\nUse this default subscription URL? (y/n) [y]: ").strip().lower()
            
            if use_default in ['', 'y', 'yes']:
                sub_url = default_url
            else:
                sub_url = input("\nPlease enter your V2Ray subscription URL: ").strip()
        else:
            sub_url = input("\nPlease enter V2Ray subscription URL: ").strip()
            
        if sub_url:
            nodes = parse_subscription(sub_url)
            if nodes:
                save_subscription(sub_url, nodes)
    else:
        nodes = [{**node, "protocol": "vmess", "uuid": DEFAULT_UUID} for node in BUILTIN_NODES]

    if not nodes:
        log("No available nodes found", "ERROR")
        return False

    # Test and select best node
    best_node = test_all_nodes(nodes[:20])  # Test only first 20 nodes
    if best_node:
        if apply_node_config(best_node):
            configure_system_proxy()
            test_proxy()
            log("\n✨ V2Ray configuration completed!", "SUCCESS")
            print(f"\nCurrent node: {best_node['name']}")
            print(f"Local SOCKS5 proxy: 127.0.0.1:10808")
            print(f"Local HTTP proxy: 127.0.0.1:10809")
            return True

    return False

def switch_node():
    """Switch node"""
    nodes = get_available_nodes()
    if not nodes:
        log("No available nodes", "ERROR")
        return
    
    # Filter out non-node entries (same logic as test_all_nodes)
    def is_valid_node(node):
        """Check if this is a valid VPN node"""
        node_name = node.get('name', '').lower()
        # Filter out subscription metadata entries
        if any(keyword in node_name for keyword in ['剩余流量', '过期时间', 'traffic', 'expire', 'remaining']):
            return False
        # Check if node has required fields
        if not node.get('server') or not node.get('port'):
            return False
        return True
    
    # Filter nodes
    valid_nodes = [node for node in nodes if is_valid_node(node)]
    
    if not valid_nodes:
        log("No valid nodes available", "ERROR")
        return

    # Display node list
    print("\n" + "="*60)
    print("Available Node List")
    print("="*60)

    # Group by region
    regions = {}
    for i, node in enumerate(valid_nodes):
        region = node.get("region", "Other")
        if region not in regions:
            regions[region] = []
        regions[region].append((i, node))

    for region, region_nodes in regions.items():
        print(f"\n[{region}]")
        for i, node in region_nodes:
            print(f"  {i+1:3d}. {node['name']:<30} {node['server']}:{node['port']}")

    print("\n" + "="*60)

    # Select node
    try:
        choice = input(f"\nPlease select node [1-{len(valid_nodes)}, 0 to return]: ").strip()
        if choice == "0":
            return

        idx = int(choice) - 1
        if 0 <= idx < len(valid_nodes):
            selected_node = valid_nodes[idx]
            print(f"\nSelected: {selected_node['name']}")

            # Test node
            print("\nTesting node latency...")
            test_result = test_node_latency(selected_node)
            if test_result["status"] == "online":
                print(f"✓ Node latency: {test_result['latency']:.1f}ms")
            else:
                print("✗ Node unreachable")
                confirm = input("\nNode may be unavailable, continue switching? (y/n): ")
                if confirm.lower() != 'y':
                    return

            # Apply configuration
            if apply_node_config(selected_node):
                print("\nVerifying connection...")
                ip_info = get_current_ip()
                print(f"Current IP: {ip_info}")
    except ValueError:
        log("Invalid input", "ERROR")

def update_subscription():
    """Update subscription"""
    # Get subscription URL from subscription_url.ini
    url = get_default_subscription_url()
    
    if not url:
        log("No subscription URL found in subscription_url.ini", "ERROR")
        # Fallback to manual input
        url = input("\nPlease enter subscription URL: ").strip()
        if not url:
            log("Subscription URL cannot be empty", "ERROR")
            return
    else:
        print(f"\nUsing subscription URL from subscription_url.ini:")
        print(f"{Colors.CYAN}{url}{Colors.END}")
        
        # Show previous subscription info if exists
        subscription = load_subscription()
        if subscription:
            old_url = subscription.get("url", "")
            update_time = subscription.get("update_time", 0)
            last_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(update_time))
            
            if old_url != url:
                print(f"\nPrevious subscription URL: {old_url}")
            print(f"Last update time: {last_update}")
        
        print("\nUpdating subscription...")

    nodes = parse_subscription(url)
    if nodes:
        save_subscription(url, nodes)

        # Display statistics
        region_count = {}
        for node in nodes:
            region = node.get("region", "Unknown")
            region_count[region] = region_count.get(region, 0) + 1

        print("\nSubscription updated successfully!")
        for region, count in region_count.items():
            print(f"  {region}: {count} nodes")

def restore_backup():
    """Restore configuration backup"""
    backups = []

    # Check available backups
    if os.path.exists(f"{CONFIG_FILE}.backup"):
        backups.append(("V2Ray configuration", CONFIG_FILE, f"{CONFIG_FILE}.backup"))

    if os.path.exists(f"{SUBSCRIPTION_FILE}.backup"):
        backups.append(("Subscription configuration", SUBSCRIPTION_FILE, f"{SUBSCRIPTION_FILE}.backup"))

    if os.path.exists("/etc/proxychains4.conf.backup"):
        backups.append(("ProxyChains4 configuration", "/etc/proxychains4.conf", "/etc/proxychains4.conf.backup"))

    if not backups:
        log("No backup files found", "WARNING")
        return

    print("\nAvailable backups:")
    for i, (name, _, _) in enumerate(backups, 1):
        print(f"{i}. {name}")

    try:
        choice = input(f"\nPlease select backup to restore [1-{len(backups)}, 0 to cancel]: ").strip()
        if choice == "0":
            return

        idx = int(choice) - 1
        if 0 <= idx < len(backups):
            name, target, backup = backups[idx]
            shutil.copy(backup, target)
            log(f"{name} restored", "SUCCESS")

            if "V2Ray" in name:
                restart = input("\nRestart V2Ray service? (y/n): ")
                if restart.lower() == 'y':
                    run_command("systemctl restart v2ray")
    except ValueError:
        log("Invalid input", "ERROR")

def reset_system_proxy():
    """Reset system proxy to default (remove all proxy settings)"""
    log("Resetting system proxy to default...", "INFO")
    
    # Stop V2Ray service
    print("\nStopping V2Ray service...")
    run_command("systemctl stop v2ray", check=False)
    run_command("systemctl disable v2ray", check=False)
    log("V2Ray service stopped and disabled", "SUCCESS")
    
    # Get actual user's home directory
    actual_user = os.environ.get('SUDO_USER', os.environ.get('USER'))
    if actual_user:
        import pwd
        user_info = pwd.getpwnam(actual_user)
        actual_home = user_info.pw_dir
    else:
        actual_home = os.path.expanduser('~')
    
    # Remove proxy settings from ~/.zshrc
    zshrc_path = os.path.join(actual_home, '.zshrc')
    if os.path.exists(zshrc_path):
        try:
            with open(zshrc_path, 'r') as f:
                lines = f.readlines()
            
            # Filter out V2Ray proxy related lines
            new_lines = []
            skip_next = False
            for line in lines:
                if skip_next:
                    skip_next = False
                    continue
                if '# V2Ray Proxy Configuration' in line:
                    skip_next = True
                    continue
                if 'source /etc/profile.d/v2ray_proxy.sh' in line:
                    continue
                new_lines.append(line)
            
            # Write back cleaned content
            with open(zshrc_path, 'w') as f:
                f.writelines(new_lines)
            
            log("Removed proxy settings from ~/.zshrc", "SUCCESS")
        except Exception as e:
            log(f"Failed to clean ~/.zshrc: {str(e)}", "WARNING")
    
    # Remove proxy configuration file
    proxy_sh = "/etc/profile.d/v2ray_proxy.sh"
    if os.path.exists(proxy_sh):
        try:
            os.remove(proxy_sh)
            log("Removed /etc/profile.d/v2ray_proxy.sh", "SUCCESS")
        except Exception as e:
            log(f"Failed to remove proxy configuration file: {str(e)}", "WARNING")
    
    # Reset ProxyChains4 to default if backup exists
    if os.path.exists("/etc/proxychains4.conf.backup"):
        try:
            shutil.copy("/etc/proxychains4.conf.backup", "/etc/proxychains4.conf")
            log("Restored ProxyChains4 to default configuration", "SUCCESS")
        except Exception as e:
            log(f"Failed to restore ProxyChains4: {str(e)}", "WARNING")
    
    print("\n" + "="*60)
    print(f"{Colors.GREEN}✓ System proxy has been reset to default{Colors.END}")
    print("="*60)
    print("\nChanges made:")
    print("  1. V2Ray service stopped and disabled")
    print("  2. Removed proxy settings from ~/.zshrc")
    print("  3. Removed /etc/profile.d/v2ray_proxy.sh")
    print("  4. Restored ProxyChains4 to default (if backup exists)")
    print("\nNote: You need to restart your terminal or run 'source ~/.zshrc'")
    print("      for the changes to take effect in current session.")

def show_help():
    """Display help information"""
    help_text = f"""
{Colors.HEADER}================================================================================
                        V2Ray Management Tool - Help Guide
================================================================================{Colors.END}

[Features]
  • Complete V2Ray installation and deployment process
  • Support subscription parsing (vmess/vless protocols)
  • 24 built-in backup nodes
  • Advanced latency testing (concurrent testing, success rate statistics)
  • System proxy configuration (environment variables, ProxyChains4)
  • Configuration backup and restore functions
  • Detailed logging

[Main Functions]

1. {Colors.BOLD}Quick Start{Colors.END}
   - One-click setup wizard for new users
   - Automatic V2Ray and dependency installation
   - Guided configuration for subscription or built-in nodes
   - Automatic selection of the best node

2. {Colors.BOLD}Node Management{Colors.END}
   - Switch nodes: Support subscription and built-in nodes
   - Test current node: Check connection status and latency
   - Test all nodes: Batch test and recommend the best node

3. {Colors.BOLD}Subscription Management{Colors.END}
   - Add/update subscription URL
   - Automatic parsing of vmess/vless links
   - Save subscription information for future use

4. {Colors.BOLD}System Configuration{Colors.END}
   - Configure system proxy environment variables
   - Sync ProxyChains4 configuration
   - Provide proxy_on/proxy_off shortcuts
   - Reset system proxy to default (remove all proxy settings)

5. {Colors.BOLD}Advanced Features{Colors.END}
   - View service status and logs
   - Backup/restore configuration files
   - Test proxy connection

[Configuration File Locations]
  - V2Ray config: /etc/v2ray/config.json
  - Subscription info: /etc/v2ray/subscription.json
  - ProxyChains4: /etc/proxychains4.conf
  - System logs: /var/log/v2ray_command.log

[Proxy Ports]
  - SOCKS5: 127.0.0.1:10808
  - HTTP: 127.0.0.1:10809

[Usage Tips]
  - First-time users should select "Quick Start"
  - Regularly update subscriptions for latest nodes
  - Use batch testing to find the best node
  - Restore backups when configuration errors occur

[Command Line Arguments]
  - proxy_status : Display current proxy status (beautified)
  - --help, -h : Display help information

[To-be-implemented Features]
  - --install : Install V2Ray only
  - --switch <n> : Quick switch to node n
  - --test : Test all nodes
  - --update : Update subscription

================================================================================
"""
    print(help_text)

def show_status():
    """Display current status"""
    print(f"\n{Colors.HEADER}V2Ray Service Status{Colors.END}")
    print("="*60)

    # Service status
    status = run_command("systemctl is-active v2ray", check=False)
    if status == "active":
        print(f"Service Status: {Colors.GREEN}Running{Colors.END}")
    else:
        print(f"Service Status: {Colors.RED}Stopped{Colors.END}")

    # Current node
    print(f"Current Node: {Colors.BOLD}{Colors.CYAN}{get_current_node_info()}{Colors.END}")

    # IP information
    if status == "active":
        print("Getting IP information...")
        ip_info = get_current_ip()
        print(f"Current IP: {ip_info}")

    # Subscription info
    subscription = load_subscription()
    if subscription:
        node_count = len(subscription.get("nodes", []))
        update_time = subscription.get("update_time", 0)
        last_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(update_time))
        print(f"\nSubscription Nodes: {node_count}")
        print(f"Last Update: {last_update}")
    else:
        print("\nSubscription Nodes: Not configured (using built-in nodes)")

    print("="*60)

def get_proxy_ip_info():
    """Get proxy IP detailed information"""
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
    """Get direct connection IP detailed information"""
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
    """Get current node detailed information"""
    # Check multiple possible config locations
    config_locations = [
        CONFIG_FILE,  # /etc/v2ray/config.json
        "/usr/local/etc/v2ray/config.json"
    ]

    config = None
    for config_path in config_locations:
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    break
        except:
            continue

    if not config:
        return None, None, None

    try:
        # Get protocol and server information
        outbound = config.get('outbounds', [{}])[0]
        protocol = outbound.get('protocol', 'unknown')

        if protocol in ['vmess', 'vless']:
            vnext = outbound.get('settings', {}).get('vnext', [{}])[0]
            server = vnext.get('address', 'unknown')
            port = vnext.get('port', 'unknown')
        else:
            return None, None, protocol

        # Find node name
        node_name = None
        all_nodes = get_available_nodes()
        for node in all_nodes:
            if node["server"] == server and node["port"] == port:
                node_name = node['name']
                break

        return node_name, f"{server}:{port}", protocol
    except:
        return None, None, None

def collect_proxy_status_data():
    """Collect proxy status data"""
    data = {}

    # Calculate running time
    from datetime import datetime
    start_time = datetime(2019, 2, 4, 23, 14, 18)
    current_time = datetime.now()
    time_diff = current_time - start_time

    total_seconds = int(time_diff.total_seconds())
    years = total_seconds // (365 * 24 * 3600)
    remaining = total_seconds % (365 * 24 * 3600)
    months = remaining // (30 * 24 * 3600)
    remaining = remaining % (30 * 24 * 3600)
    days = remaining // (24 * 3600)
    remaining = remaining % (24 * 3600)
    hours = remaining // 3600
    remaining = remaining % 3600
    minutes = remaining // 60
    seconds = remaining % 60

    time_parts = []
    if years > 0:
        time_parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months > 0:
        time_parts.append(f"{months} month{'s' if months != 1 else ''}")
    if days > 0:
        time_parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        time_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        time_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0:
        time_parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    data['time_str'] = " ".join(time_parts)

    # Get V2Ray service status
    data['v2ray_status'] = run_command("systemctl is-active v2ray", check=False)

    # Get node information
    data['node_name'], data['server_port'], data['protocol'] = get_current_node_detail()

    # Test current node latency
    data['latency_result'] = None
    if data['server_port']:
        try:
            server, port = data['server_port'].split(':')
            current_node = {
                "server": server,
                "port": int(port),
                "name": data['node_name'] or 'Unknown',
                "region": data['node_name'].split(' - ')[0] if data['node_name'] and ' - ' in data['node_name'] else ''
            }
            data['latency_result'] = test_node_latency(current_node, timeout=3, test_count=2)
        except:
            pass

    # Check proxy environment variables
    data['http_proxy'] = os.environ.get('http_proxy', '')
    data['https_proxy'] = os.environ.get('https_proxy', '')
    data['all_proxy'] = os.environ.get('all_proxy', '')

    # Get IP information
    data['proxy_info'] = None
    data['direct_info'] = None

    if data['v2ray_status'] == "active":
        data['proxy_info'] = get_proxy_ip_info()
        data['direct_info'] = get_direct_ip_info()
    else:
        data['direct_info'] = get_direct_ip_info()

    return data

def render_proxy_status(data, refresh_mode=False):
    """Render proxy status display"""
    output = []

    output.append("")
    output.append(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.END}")
    output.append(f"{Colors.CYAN}║                    🌐 V2Ray Proxy Status                     ║{Colors.END}")
    output.append(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.END}")

    # Running time
    output.append(f"{Colors.BLUE}▸ Running Time: {Colors.GREEN}{data['time_str']}{Colors.END}")

    # V2Ray service status
    if data['v2ray_status'] == "active":
        output.append(f"{Colors.GREEN}▸ V2Ray Service: ✓ Running{Colors.END}")
    else:
        output.append(f"{Colors.RED}▸ V2Ray Service: ✗ Stopped{Colors.END}")

    # Node information
    if data['node_name']:
        output.append(f"{Colors.BLUE}▸ Current Node: {Colors.BOLD}{Colors.CYAN}🔸 {data['node_name']} 🔸{Colors.END}")
        output.append(f"{Colors.BLUE}▸ Server: {Colors.END}{data['server_port']} {Colors.PURPLE}[{data['protocol']}]{Colors.END}")

        # Node latency
        if data['latency_result']:
            if data['latency_result']['status'] == 'online':
                latency = data['latency_result']['latency']
                if latency <= 80:
                    color = Colors.GREEN
                elif latency <= 150:
                    color = Colors.YELLOW
                else:
                    color = Colors.RED
                output.append(f"{Colors.BLUE}▸ Node Latency: {color}{latency:.1f}ms{Colors.END}")
            else:
                output.append(f"{Colors.BLUE}▸ Node latency: {Colors.RED}Unreachable{Colors.END} {Colors.RED}[Offline]{Colors.END}")
    elif data['server_port']:
        output.append(f"{Colors.BLUE}▸ Current node: {Colors.BOLD}{Colors.RED}Unknown Node{Colors.END}")
        output.append(f"{Colors.BLUE}▸ Server: {Colors.END}{data['server_port']} {Colors.PURPLE}[{data['protocol']}]{Colors.END}")
    else:
        output.append(f"{Colors.RED}▸ Node Status: Not configured{Colors.END}")

    # Proxy environment variables
    output.append("")
    if data['http_proxy'] or data['https_proxy'] or data['all_proxy']:
        output.append(f"{Colors.GREEN}▸ Terminal Proxy: ✓ Configured{Colors.END}")
        if data['http_proxy']:
            output.append(f"  {Colors.BLUE}HTTP:{Colors.END}  {data['http_proxy']}")
        if data['https_proxy']:
            output.append(f"  {Colors.BLUE}HTTPS:{Colors.END} {data['https_proxy']}")
        if data['all_proxy']:
            output.append(f"  {Colors.BLUE}SOCKS:{Colors.END} {data['all_proxy']}")
    else:
        output.append(f"{Colors.YELLOW}▸ Terminal Proxy: ⚠ Not configured{Colors.END}")

    # IP information
    output.append("")
    output.append(f"{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")

    proxy_failed = False
    if data['v2ray_status'] == "active":
        if data['proxy_info']:
            proxy_ip = data['proxy_info'].get('ip', 'Unknown')
            proxy_country = data['proxy_info'].get('country', '')
            proxy_city = data['proxy_info'].get('city', '')
            proxy_org = data['proxy_info'].get('org', '')

            output.append(f"{Colors.GREEN}▸ Proxy IP: {Colors.YELLOW}{proxy_ip}{Colors.END} {Colors.BLUE}({proxy_country} {proxy_city}){Colors.END}")
            output.append(f"{Colors.GREEN}▸ ISP: {Colors.END}{proxy_org}")
        else:
            output.append(f"{Colors.RED}▸ Proxy Connection: ✗ Unable to connect to proxy server{Colors.END}")
            proxy_failed = True

        if data['direct_info']:
            direct_ip = data['direct_info'].get('ip', 'Unknown')
            direct_country = data['direct_info'].get('country', '')
            output.append(f"{Colors.BLUE}▸ Local IP: {Colors.END}{direct_ip} {Colors.PURPLE}({direct_country}){Colors.END}")
    else:
        if data['direct_info']:
            direct_ip = data['direct_info'].get('ip', 'Unknown')
            direct_country = data['direct_info'].get('country', '')
            direct_city = data['direct_info'].get('city', '')
            output.append(f"{Colors.BLUE}▸ Current IP: {Colors.END}{direct_ip} {Colors.PURPLE}({direct_country} {direct_city}){Colors.END}")

    output.append(f"{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")

    # Quick tips
    if proxy_failed:
        output.append("")
        output.append(f"{Colors.PURPLE}💡 Quick Commands:{Colors.END}")
        output.append(f"  {Colors.BLUE}▸{Colors.END} Switch Node: {Colors.YELLOW}python3 {sys.argv[0]}{Colors.END}")
        output.append(f"  {Colors.BLUE}▸{Colors.END} Check Status: {Colors.YELLOW}sudo systemctl status v2ray{Colors.END}")
        output.append(f"  {Colors.BLUE}▸{Colors.END} Restart Service: {Colors.YELLOW}sudo systemctl restart v2ray{Colors.END}")
        output.append("")
    else:
        output.append("")

    # Refresh mode prompt
    if refresh_mode:
        output.append(f"{Colors.PURPLE}Press Ctrl+C to exit{Colors.END}")

    return "\n".join(output)

def show_proxy_status(refresh_mode=False):
    """Display proxy status (beautified version)

    Args:
        refresh_mode: Enable auto-refresh mode, refresh every 3 seconds
    """
    # Collect data
    data = collect_proxy_status_data()
    # Render and display
    print(render_proxy_status(data, refresh_mode))

def show_main_menu():
    """Display main menu"""
    print(f"\n{Colors.BOLD}V2Ray Management Tool v2.1{Colors.END}")
    print("="*60)
    print(f"Current Node: {Colors.BOLD}{Colors.CYAN}{get_current_node_info()}{Colors.END}")
    print("="*60)
    print("1. Quick Start (recommended for new users)")
    print("2. Node Management")
    print("   21. Switch Node")
    print("   22. Test Current Node")
    print("   23. Test All Nodes")
    print("3. Subscription Management")
    print("   31. Update Subscription")
    print("4. System Configuration")
    print("   41. Configure System Proxy")
    print("   42. Sync ProxyChains4")
    print("   43. Reset System Proxy to Default")
    print("5. Advanced Features")
    print("   51. View Service Status")
    print("   52. Test Proxy Connection")
    print("   53. Restore Configuration Backup")
    print("   54. View Logs")
    print("   55. Show Proxy Status (beautified)")
    print("   56. Real-time Monitor Proxy Status (3s refresh)")
    print("6. Help")
    print("0. Exit")
    print("="*60)

def main():
    """Main function"""
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "proxy_status":
            # Display proxy status directly and exit
            show_proxy_status()
            return 0
        elif sys.argv[1] == "proxy_status_refresh":
            # Enter real-time refresh mode
            try:
                while True:
                    # Collect data first
                    data = collect_proxy_status_data()
                    # Then clear screen and display
                    os.system('clear')
                    print(render_proxy_status(data, refresh_mode=True))
                    time.sleep(3)
            except KeyboardInterrupt:
                print("\n\nExiting monitor mode...")
                return 0
        elif sys.argv[1] in ["--help", "-h"]:
            print(f"Usage: {sys.argv[0]} [options]")
            print("\nOptions:")
            print("  proxy_status         Display current proxy status information")
            print("  proxy_status_refresh Real-time monitor proxy status (3s refresh)")
            print("  --help, -h           Display this help information")
            print("\nEnter interactive menu when no arguments provided")
            return 0

    # Enter interactive menu
    print(f"{Colors.HEADER}V2Ray Management Tool{Colors.END}")
    print(f"Version: 2.1.0 | Platform: Ubuntu/Debian\n")

    while True:
        show_main_menu()
        choice = input("Please select operation: ").strip()

        try:
            if choice == "0":
                print("\nThank you for using!")
                break

            elif choice == "1":
                # Quick start
                quick_start()

            elif choice == "21":
                # Switch node
                switch_node()

            elif choice == "22":
                # Test current node
                nodes = get_available_nodes()
                current_node = None

                # Find current node
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
                    print(f"\nCurrent node: {current_node['name']}")
                    result = test_node_latency(current_node, test_count=5)
                    if result["status"] == "online":
                        print(f"✓ Status: {result['status']}")
                        print(f"✓ Latency: {result['latency']:.1f}ms")
                        print(f"✓ Success rate: {result['success_rate']:.0f}%")
                    else:
                        print(f"✗ Node is offline")
                else:
                    log("Unable to identify current node", "ERROR")

            elif choice == "23":
                # Test all nodes
                nodes = get_available_nodes()
                test_all_nodes(nodes)

            elif choice == "31":
                # Update subscription
                update_subscription()

            elif choice == "41":
                # Configure system proxy
                configure_system_proxy()

            elif choice == "42":
                # Sync ProxyChains4
                run_command("sudo sed -i 's/socks5  127.0.0.1 1080/socks5  127.0.0.1 10808/g' /etc/proxychains4.conf")
                log("ProxyChains4 configuration synchronized", "SUCCESS")

            elif choice == "43":
                # Reset system proxy to default
                confirm = input("\nAre you sure you want to reset system proxy to default? This will:\n"
                              "- Stop and disable V2Ray service\n"
                              "- Remove all proxy settings from ~/.zshrc\n"
                              "- Remove proxy environment configurations\n"
                              "\nContinue? (y/n): ").strip().lower()
                if confirm == 'y':
                    reset_system_proxy()

            elif choice == "51":
                # View service status
                show_status()

            elif choice == "52":
                # Test proxy
                test_proxy()

            elif choice == "53":
                # Restore backup
                restore_backup()

            elif choice == "54":
                # View logs
                if os.path.exists(LOG_FILE):
                    run_command(f"tail -n 50 {LOG_FILE}", capture_output=False)
                else:
                    log("Log file does not exist", "WARNING")

            elif choice == "55":
                # Show proxy status (beautified)
                show_proxy_status()

            elif choice == "56":
                # Real-time monitor proxy status
                print("\nEntering real-time monitoring mode, refreshing every 3 seconds...")
                print("Press Ctrl+C to exit monitoring")
                time.sleep(1)
                try:
                    while True:
                        # Collect data first
                        data = collect_proxy_status_data()
                        # Then clear screen and display
                        os.system('clear')
                        print(render_proxy_status(data, refresh_mode=True))
                        time.sleep(3)
                except KeyboardInterrupt:
                    print("\n\nExited monitoring mode")

            elif choice == "6":
                # Help
                show_help()

            else:
                log("Invalid choice", "WARNING")

            if choice != "0":
                input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\nOperation cancelled")
            break
        except Exception as e:
            log(f"Error occurred: {str(e)}", "ERROR")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled")
        sys.exit(1)
    except Exception as e:
        log(f"Error occurred: {str(e)}", "ERROR")
        sys.exit(1)
