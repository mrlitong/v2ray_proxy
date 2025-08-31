#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V2Ray Cross-Platform Management Tool
Supports both macOS and Linux (Ubuntu/Debian) with full feature parity

Features:
1. Complete V2Ray installation and deployment
2. Subscription management (supports vmess/vless)
3. Node switching and management (supports subscription nodes and built-in nodes)
4. Advanced latency testing
5. System proxy configuration
6. ProxyChains4/proxychains-ng synchronization
7. Configuration backup and restore
8. Detailed logging
9. Beautified proxy status display
10. Cross-platform support (macOS, Linux)

Author: Claude Assistant
Version: 3.0.0
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
import platform
import abc
from urllib.parse import urlparse, unquote, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# ==================== Platform Detection ====================
PLATFORM = platform.system().lower()
IS_MACOS = PLATFORM == 'darwin'
IS_LINUX = PLATFORM == 'linux'

# ==================== Global Configuration ====================
class Config:
    """Platform-specific configuration"""
    def __init__(self):
        if IS_MACOS:
            self.CONFIG_DIR = "/usr/local/etc/v2ray"
            self.LOG_DIR = "/usr/local/var/log"
            self.V2RAY_BIN = "/usr/local/bin/v2ray"
            self.V2RAY_SHARE = "/usr/local/share/v2ray"
            self.SERVICE_NAME = "com.v2ray.core"
            self.PROXYCHAINS_CONFIG = "/usr/local/etc/proxychains-ng.conf"
            self.SHELL_CONFIG_DIR = "/etc/profile.d"  # Will use ~/.zshrc for macOS
        else:  # Linux
            self.CONFIG_DIR = "/etc/v2ray"
            self.LOG_DIR = "/var/log"
            self.V2RAY_BIN = "/usr/local/bin/v2ray"
            self.V2RAY_SHARE = "/usr/local/share/v2ray"
            self.SERVICE_NAME = "v2ray"
            self.PROXYCHAINS_CONFIG = "/etc/proxychains4.conf"
            self.SHELL_CONFIG_DIR = "/etc/profile.d"
        
        self.CONFIG_FILE = os.path.join(self.CONFIG_DIR, "config.json")
        self.SUBSCRIPTION_FILE = os.path.join(self.CONFIG_DIR, "subscription.json")
        self.LOG_FILE = os.path.join(self.LOG_DIR, "v2ray_command.log")

CONFIG = Config()

# ==================== Color Output ====================
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

# ==================== Built-in Nodes ====================
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

DEFAULT_UUID = "39a279a5-55bb-3a27-ad9b-6ec81ff5779a"

# ==================== Logging ====================
def log(message, level="INFO"):
    """Log messages"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"

    # Write to log file
    try:
        os.makedirs(os.path.dirname(CONFIG.LOG_FILE), exist_ok=True)
        with open(CONFIG.LOG_FILE, 'a', encoding='utf-8') as f:
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

# ==================== Platform Abstraction ====================
class PlatformHandler(abc.ABC):
    """Abstract base class for platform-specific operations"""
    
    @abc.abstractmethod
    def check_system(self):
        """Check if system is supported"""
        pass
    
    @abc.abstractmethod
    def install_dependencies(self):
        """Install system dependencies"""
        pass
    
    @abc.abstractmethod
    def install_v2ray(self):
        """Install V2Ray"""
        pass
    
    @abc.abstractmethod
    def create_service(self):
        """Create system service"""
        pass
    
    @abc.abstractmethod
    def start_service(self):
        """Start V2Ray service"""
        pass
    
    @abc.abstractmethod
    def stop_service(self):
        """Stop V2Ray service"""
        pass
    
    @abc.abstractmethod
    def restart_service(self):
        """Restart V2Ray service"""
        pass
    
    @abc.abstractmethod
    def enable_service(self):
        """Enable service auto-start"""
        pass
    
    @abc.abstractmethod
    def disable_service(self):
        """Disable service auto-start"""
        pass
    
    @abc.abstractmethod
    def is_service_active(self):
        """Check if service is active"""
        pass
    
    @abc.abstractmethod
    def configure_proxychains(self):
        """Configure ProxyChains"""
        pass

class MacOSHandler(PlatformHandler):
    """macOS-specific implementations"""
    
    def check_system(self):
        """Check macOS system"""
        log(f"Detected macOS {platform.mac_ver()[0]}", "INFO")
        
        # Check if running with sufficient privileges for certain operations
        if os.geteuid() != 0:
            log("Note: Some operations may require sudo privileges", "WARNING")
        
        # Check network
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
        except:
            log("Network connection error, please check network settings", "ERROR")
            return False
        
        return True
    
    def install_dependencies(self):
        """Install dependencies via Homebrew"""
        log("Checking Homebrew installation...", "INFO")
        
        # Check if Homebrew is installed
        if run_command("which brew", check=False) is None:
            log("Homebrew not found. Installing Homebrew...", "INFO")
            install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            run_command(install_cmd, capture_output=False)
        
        dependencies = {
            "curl": "curl",
            "wget": "wget",
            "jq": "jq",
            "proxychains-ng": "proxychains-ng"
        }
        
        for cmd, package in dependencies.items():
            if run_command(f"which {cmd}", check=False):
                log(f"{package} already installed", "SUCCESS")
            else:
                log(f"Installing {package}...", "INFO")
                run_command(f"brew install {package}", capture_output=False)
    
    def install_v2ray(self):
        """Install V2Ray on macOS"""
        log("Starting V2Ray installation for macOS...", "INFO")
        
        # Check if already installed
        if os.path.exists(CONFIG.V2RAY_BIN):
            v2ray_version = run_command(f"{CONFIG.V2RAY_BIN} version | head -1", check=False)
            if v2ray_version:
                log(f"V2Ray already installed: {v2ray_version}", "SUCCESS")
                return True
        
        # Method 1: Try Homebrew first
        log("Installing V2Ray via Homebrew...", "INFO")
        result = run_command("brew install v2ray", capture_output=False, check=False)
        
        if result and result.returncode == 0:
            log("V2Ray installed successfully via Homebrew", "SUCCESS")
            os.makedirs(CONFIG.CONFIG_DIR, exist_ok=True)
            return True
        
        # Method 2: Manual installation
        log("Installing V2Ray manually...", "INFO")
        
        # Download V2Ray for macOS
        download_url = "https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-macos-64.zip"
        temp_dir = tempfile.mkdtemp()
        zip_file = os.path.join(temp_dir, "v2ray-macos.zip")
        
        try:
            log("Downloading V2Ray...", "INFO")
            run_command(f"curl -L -o {zip_file} {download_url}", capture_output=False)
            
            # Extract files
            log("Extracting V2Ray files...", "INFO")
            run_command(f"unzip -o {zip_file} -d {temp_dir}")
            
            # Create directories
            os.makedirs(os.path.dirname(CONFIG.V2RAY_BIN), exist_ok=True)
            os.makedirs(CONFIG.V2RAY_SHARE, exist_ok=True)
            os.makedirs(CONFIG.CONFIG_DIR, exist_ok=True)
            os.makedirs(CONFIG.LOG_DIR, exist_ok=True)
            
            # Copy files
            shutil.copy(os.path.join(temp_dir, "v2ray"), CONFIG.V2RAY_BIN)
            os.chmod(CONFIG.V2RAY_BIN, 0o755)
            
            # Copy data files if they exist
            for data_file in ["geoip.dat", "geosite.dat"]:
                if os.path.exists(os.path.join(temp_dir, data_file)):
                    shutil.copy(os.path.join(temp_dir, data_file), CONFIG.V2RAY_SHARE)
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
            log("V2Ray installed successfully", "SUCCESS")
            return True
            
        except Exception as e:
            log(f"Failed to install V2Ray: {str(e)}", "ERROR")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return False
    
    def create_service(self):
        """Create launchd service for macOS"""
        plist_path = f"/Library/LaunchDaemons/{CONFIG.SERVICE_NAME}.plist"
        
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{CONFIG.SERVICE_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{CONFIG.V2RAY_BIN}</string>
        <string>run</string>
        <string>-config</string>
        <string>{CONFIG.CONFIG_FILE}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>{CONFIG.LOG_FILE}.error</string>
    <key>StandardOutPath</key>
    <string>{CONFIG.LOG_FILE}.out</string>
    <key>WorkingDirectory</key>
    <string>{CONFIG.CONFIG_DIR}</string>
</dict>
</plist>"""
        
        try:
            # Need sudo to write to /Library/LaunchDaemons/
            with tempfile.NamedTemporaryFile(mode='w', suffix='.plist', delete=False) as f:
                f.write(plist_content)
                temp_plist = f.name
            
            run_command(f"sudo cp {temp_plist} {plist_path}")
            run_command(f"sudo chown root:wheel {plist_path}")
            run_command(f"sudo chmod 644 {plist_path}")
            os.unlink(temp_plist)
            
            log("V2Ray launchd service created", "SUCCESS")
            return True
        except Exception as e:
            log(f"Failed to create launchd service: {str(e)}", "ERROR")
            return False
    
    def start_service(self):
        """Start V2Ray service on macOS"""
        return run_command(f"sudo launchctl load /Library/LaunchDaemons/{CONFIG.SERVICE_NAME}.plist", check=False)
    
    def stop_service(self):
        """Stop V2Ray service on macOS"""
        return run_command(f"sudo launchctl unload /Library/LaunchDaemons/{CONFIG.SERVICE_NAME}.plist", check=False)
    
    def restart_service(self):
        """Restart V2Ray service on macOS"""
        self.stop_service()
        time.sleep(1)
        self.start_service()
    
    def enable_service(self):
        """Enable service auto-start on macOS"""
        # launchd services with RunAtLoad=true start automatically
        return True
    
    def disable_service(self):
        """Disable service auto-start on macOS"""
        self.stop_service()
        return True
    
    def is_service_active(self):
        """Check if V2Ray service is running on macOS"""
        result = run_command(f"sudo launchctl list | grep {CONFIG.SERVICE_NAME}", check=False)
        return result is not None and CONFIG.SERVICE_NAME in result
    
    def configure_proxychains(self):
        """Configure proxychains-ng for macOS"""
        proxychains_config = CONFIG.PROXYCHAINS_CONFIG
        
        if not os.path.exists(proxychains_config):
            # Create default configuration
            config_content = """# proxychains-ng config for V2Ray
strict_chain
proxy_dns
remote_dns_subnet 224
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
socks5 127.0.0.1 10808
"""
            try:
                os.makedirs(os.path.dirname(proxychains_config), exist_ok=True)
                with open(proxychains_config, 'w') as f:
                    f.write(config_content)
                log("Created proxychains-ng configuration", "SUCCESS")
            except Exception as e:
                log(f"Failed to create proxychains-ng config: {str(e)}", "WARNING")
        else:
            # Update existing configuration
            try:
                with open(proxychains_config, 'r') as f:
                    content = f.read()
                
                # Update proxy settings
                if 'socks5  127.0.0.1 10808' not in content:
                    content = content.replace('socks5  127.0.0.1 1080', 'socks5  127.0.0.1 10808')
                    content = content.replace('socks4 	127.0.0.1 9050', 'socks5  127.0.0.1 10808')
                    
                    with open(proxychains_config, 'w') as f:
                        f.write(content)
                    log("Updated proxychains-ng configuration", "SUCCESS")
            except Exception as e:
                log(f"Failed to update proxychains-ng config: {str(e)}", "WARNING")

class LinuxHandler(PlatformHandler):
    """Linux-specific implementations"""
    
    def check_system(self):
        """Check Linux system"""
        log("Checking system environment...", "INFO")
        
        # Check operating system
        if not os.path.exists("/etc/os-release"):
            log("Unsupported operating system", "ERROR")
            return False
        
        os_info = run_command("cat /etc/os-release | grep -E '^(ID|VERSION_ID)='")
        if "ubuntu" not in os_info.lower() and "debian" not in os_info.lower():
            log("Warning: This script is optimized for Ubuntu/Debian", "WARNING")
        
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
    
    def install_dependencies(self):
        """Install dependencies via apt-get"""
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
    
    def install_v2ray(self):
        """Install V2Ray on Linux"""
        log("Starting V2Ray installation...", "INFO")
        
        # Check if already installed
        if os.path.exists(CONFIG.V2RAY_BIN):
            v2ray_version = run_command(f"{CONFIG.V2RAY_BIN} version | head -1", check=False)
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
                os.makedirs(os.path.dirname(CONFIG.V2RAY_BIN), exist_ok=True)
                os.makedirs(CONFIG.V2RAY_SHARE, exist_ok=True)
                os.makedirs(CONFIG.CONFIG_DIR, exist_ok=True)
                os.makedirs(CONFIG.LOG_DIR, exist_ok=True)
                
                # Extract zip file
                log("Extracting V2Ray files...", "INFO")
                run_command(f"unzip -o {local_zip} -d /tmp/v2ray-temp")
                
                # Copy binary files
                run_command(f"cp /tmp/v2ray-temp/v2ray {CONFIG.V2RAY_BIN}")
                run_command(f"chmod +x {CONFIG.V2RAY_BIN}")
                
                # Copy other files
                if os.path.exists("/tmp/v2ray-temp/geoip.dat"):
                    run_command(f"cp /tmp/v2ray-temp/geoip.dat {CONFIG.V2RAY_SHARE}/")
                if os.path.exists("/tmp/v2ray-temp/geosite.dat"):
                    run_command(f"cp /tmp/v2ray-temp/geosite.dat {CONFIG.V2RAY_SHARE}/")
                
                # Cleanup
                run_command("rm -rf /tmp/v2ray-temp")
                
                log("V2Ray installed successfully from local file", "SUCCESS")
                self.create_service()
                return True
                
            except Exception as e:
                log(f"Local installation failed: {str(e)}", "ERROR")
                log("Falling back to online installation...", "INFO")
        
        # Online installation
        log("Downloading V2Ray installation script...", "INFO")
        install_script = "/tmp/install-release.sh"
        run_command(f"wget -O {install_script} https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh")
        run_command(f"chmod +x {install_script}")
        
        # Execute installation
        log("Installing V2Ray...", "INFO")
        run_command(f"bash {install_script}", capture_output=False)
        
        # Create configuration directory
        os.makedirs(CONFIG.CONFIG_DIR, exist_ok=True)
        
        # Fix configuration path in systemd service file if needed
        self._fix_systemd_config_path()
        
        # Cleanup
        os.remove(install_script)
        
        log("V2Ray installation completed", "SUCCESS")
        return True
    
    def _fix_systemd_config_path(self):
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
                content = content.replace("/usr/local/etc/v2ray/config.json", CONFIG.CONFIG_FILE)
                
                # Write back
                with open(service_file, 'w') as f:
                    f.write(content)
                
                # Reload systemd
                run_command("systemctl daemon-reload")
                log("V2Ray service config path fixed", "SUCCESS")
        except Exception as e:
            log(f"Failed to fix service config path: {str(e)}", "WARNING")
    
    def create_service(self):
        """Create systemd service for Linux"""
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
        try:
            with open("/etc/systemd/system/v2ray.service", "w") as f:
                f.write(service_content)
            
            # Reload systemd
            run_command("systemctl daemon-reload")
            log("V2Ray systemd service created", "SUCCESS")
            return True
        except Exception as e:
            log(f"Failed to create systemd service: {str(e)}", "ERROR")
            return False
    
    def start_service(self):
        """Start V2Ray service on Linux"""
        run_command("systemctl daemon-reload")
        return run_command("systemctl start v2ray", check=False)
    
    def stop_service(self):
        """Stop V2Ray service on Linux"""
        return run_command("systemctl stop v2ray", check=False)
    
    def restart_service(self):
        """Restart V2Ray service on Linux"""
        run_command("systemctl daemon-reload")
        return run_command("systemctl restart v2ray", check=False)
    
    def enable_service(self):
        """Enable service auto-start on Linux"""
        return run_command("systemctl enable v2ray", check=False)
    
    def disable_service(self):
        """Disable service auto-start on Linux"""
        return run_command("systemctl disable v2ray", check=False)
    
    def is_service_active(self):
        """Check if V2Ray service is running on Linux"""
        status = run_command("systemctl is-active v2ray", check=False)
        return status == "active"
    
    def configure_proxychains(self):
        """Configure ProxyChains4 for Linux"""
        proxychains_config = CONFIG.PROXYCHAINS_CONFIG
        
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
                content = content.replace('socks4 	127.0.0.1 9050', 'socks5  127.0.0.1 10808')
                content = content.replace('socks5  127.0.0.1 1080', 'socks5  127.0.0.1 10808')
            
            with open(proxychains_config, 'w') as f:
                f.write(content)
            
            log("ProxyChains4 configuration completed", "SUCCESS")

# ==================== Platform Handler Factory ====================
def get_platform_handler():
    """Get the appropriate platform handler"""
    if IS_MACOS:
        return MacOSHandler()
    elif IS_LINUX:
        return LinuxHandler()
    else:
        raise NotImplementedError(f"Platform {PLATFORM} is not supported")

# Global platform handler
PLATFORM_HANDLER = get_platform_handler()

# ==================== Core Functions (Platform-independent) ====================

def check_system():
    """Check system compatibility"""
    return PLATFORM_HANDLER.check_system()

def install_dependencies():
    """Install system dependencies"""
    PLATFORM_HANDLER.install_dependencies()

def install_v2ray():
    """Install V2Ray"""
    return PLATFORM_HANDLER.install_v2ray()

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
        "Hong Kong": ["hk", "hong kong", "hongkong", "香港"],
        "Japan": ["jp", "japan", "tokyo", "日本"],
        "Singapore": ["sg", "singapore", "新加坡"],
        "USA": ["us", "america", "usa", "美国"],
        "Korea": ["kr", "korea", "seoul", "韩国"],
        "Taiwan": ["tw", "taiwan", "台湾"],
        "Canada": ["ca", "canada", "加拿大"],
        "UK": ["uk", "britain", "london", "英国"],
        "Germany": ["de", "germany", "frankfurt", "德国"],
        "India": ["in", "india", "mumbai", "印度"],
        "Russia": ["ru", "russia", "moscow", "俄罗斯"]
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
    REGION_WIDTH = 10
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
    
    # Configure ProxyChains
    PLATFORM_HANDLER.configure_proxychains()
    
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
    
    # Get the actual user's home directory
    actual_user = os.environ.get('SUDO_USER', os.environ.get('USER'))
    if actual_user:
        import pwd
        try:
            user_info = pwd.getpwnam(actual_user)
            actual_home = user_info.pw_dir
            actual_uid = user_info.pw_uid
            actual_gid = user_info.pw_gid
        except:
            actual_home = os.path.expanduser('~')
            actual_uid = os.getuid()
            actual_gid = os.getgid()
    else:
        actual_home = os.path.expanduser('~')
        actual_uid = os.getuid()
        actual_gid = os.getgid()
    
    # Determine shell config file
    user_shell = os.environ.get('SHELL', '/bin/bash')
    
    if 'zsh' in user_shell:
        shell_rc = '.zshrc'
    elif 'bash' in user_shell:
        shell_rc = '.bashrc'
    else:
        shell_rc = '.profile'
    
    rc_path = os.path.join(actual_home, shell_rc)
    
    # Check if proxy config already exists
    proxy_marker = '# V2Ray Proxy Configuration'
    
    try:
        if os.path.exists(rc_path):
            with open(rc_path, 'r') as f:
                content = f.read()
            
            if proxy_marker not in content:
                # Add proxy configuration
                with open(rc_path, 'a') as f:
                    f.write(f'\n{shell_config}\n')
                log(f"Added proxy configuration to ~/{shell_rc}", "SUCCESS")
            else:
                log(f"Proxy configuration already exists in ~/{shell_rc}", "INFO")
        else:
            # Create new rc file
            with open(rc_path, 'w') as f:
                f.write(shell_config)
            log(f"Created ~/{shell_rc} with proxy configuration", "SUCCESS")
        
        # Set proper ownership
        if IS_LINUX and os.geteuid() == 0:
            os.chown(rc_path, actual_uid, actual_gid)
    
    except Exception as e:
        log(f"Failed to configure shell proxy: {str(e)}", "WARNING")
    
    log("System proxy environment variables configured", "SUCCESS")
    log("New terminals will automatically load proxy settings", "INFO")
    log("Use proxy_on/proxy_off/proxy_status to control proxy", "INFO")
    log(f"For current session, run: source ~/{shell_rc}", "INFO")

def save_subscription(url, nodes):
    """Save subscription information"""
    subscription_data = {
        "url": url,
        "nodes": nodes,
        "update_time": int(time.time()),
        "selected_index": 0
    }

    # Backup existing configuration
    if os.path.exists(CONFIG.SUBSCRIPTION_FILE):
        shutil.copy(CONFIG.SUBSCRIPTION_FILE, f"{CONFIG.SUBSCRIPTION_FILE}.backup")

    with open(CONFIG.SUBSCRIPTION_FILE, 'w', encoding='utf-8') as f:
        json.dump(subscription_data, f, indent=2, ensure_ascii=False)

    log("Subscription information saved", "SUCCESS")

def load_subscription():
    """Load subscription information"""
    try:
        if os.path.exists(CONFIG.SUBSCRIPTION_FILE):
            with open(CONFIG.SUBSCRIPTION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        log(f"Failed to load subscription configuration: {str(e)}", "ERROR")
        return None

def apply_node_config(node):
    """Apply node configuration"""
    # Generate new configuration
    config = generate_v2ray_config(node)
    
    # Create config directory if not exists
    os.makedirs(CONFIG.CONFIG_DIR, exist_ok=True)
    
    # Backup current configuration if exists
    if os.path.exists(CONFIG.CONFIG_FILE):
        shutil.copy(CONFIG.CONFIG_FILE, f"{CONFIG.CONFIG_FILE}.backup")
    
    # Save configuration
    try:
        with open(CONFIG.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        log(f"Configuration saved to: {CONFIG.CONFIG_FILE}", "INFO")
    except Exception as e:
        log(f"Failed to save config: {str(e)}", "ERROR")
        return False
    
    # Verify configuration
    result = run_command(f"{CONFIG.V2RAY_BIN} test -config {CONFIG.CONFIG_FILE}", check=False)
    if result and "Configuration OK" in result:
        log("Configuration validation passed", "SUCCESS")
    else:
        log("Configuration validation failed, restoring backup", "ERROR")
        if os.path.exists(f"{CONFIG.CONFIG_FILE}.backup"):
            shutil.copy(f"{CONFIG.CONFIG_FILE}.backup", CONFIG.CONFIG_FILE)
        return False
    
    # Create service if not exists (for macOS)
    if IS_MACOS and not PLATFORM_HANDLER.is_service_active():
        PLATFORM_HANDLER.create_service()
    
    # Restart service
    PLATFORM_HANDLER.enable_service()
    PLATFORM_HANDLER.restart_service()
    
    # Check service status
    time.sleep(2)
    if PLATFORM_HANDLER.is_service_active():
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
    config = None
    
    try:
        if os.path.exists(CONFIG.CONFIG_FILE):
            with open(CONFIG.CONFIG_FILE, 'r') as f:
                config = json.load(f)
    except:
        pass
    
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
    print(f"Platform: {Colors.CYAN}{platform.system()} {platform.release()}{Colors.END}")
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
            
            # Platform-specific tips
            if IS_MACOS:
                print(f"\n{Colors.YELLOW}macOS Tips:{Colors.END}")
                print("• Use 'proxychains4' command to proxy terminal apps")
                print("• Configure system proxy in System Preferences > Network > Advanced > Proxies")
                print("• Or use proxy auto-configuration (PAC) for automatic switching")
            else:
                print(f"\n{Colors.YELLOW}Linux Tips:{Colors.END}")
                print("• Use 'proxychains4' command to proxy terminal apps")
                print("• Environment variables will be set in new terminals")
            
            return True
    
    return False

def switch_node():
    """Switch node"""
    nodes = get_available_nodes()
    if not nodes:
        log("No available nodes", "ERROR")
        return
    
    # Filter out non-node entries
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
    if os.path.exists(f"{CONFIG.CONFIG_FILE}.backup"):
        backups.append(("V2Ray configuration", CONFIG.CONFIG_FILE, f"{CONFIG.CONFIG_FILE}.backup"))

    if os.path.exists(f"{CONFIG.SUBSCRIPTION_FILE}.backup"):
        backups.append(("Subscription configuration", CONFIG.SUBSCRIPTION_FILE, f"{CONFIG.SUBSCRIPTION_FILE}.backup"))

    if os.path.exists(f"{CONFIG.PROXYCHAINS_CONFIG}.backup"):
        proxychains_name = "proxychains-ng" if IS_MACOS else "ProxyChains4"
        backups.append((f"{proxychains_name} configuration", CONFIG.PROXYCHAINS_CONFIG, f"{CONFIG.PROXYCHAINS_CONFIG}.backup"))

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
                    PLATFORM_HANDLER.restart_service()
    except ValueError:
        log("Invalid input", "ERROR")

def reset_system_proxy():
    """Reset system proxy to default (remove all proxy settings)"""
    log("Resetting system proxy to default...", "INFO")
    
    # Stop V2Ray service
    print("\nStopping V2Ray service...")
    PLATFORM_HANDLER.stop_service()
    PLATFORM_HANDLER.disable_service()
    log("V2Ray service stopped and disabled", "SUCCESS")
    
    # Get actual user's home directory
    actual_user = os.environ.get('SUDO_USER', os.environ.get('USER'))
    if actual_user:
        import pwd
        try:
            user_info = pwd.getpwnam(actual_user)
            actual_home = user_info.pw_dir
        except:
            actual_home = os.path.expanduser('~')
    else:
        actual_home = os.path.expanduser('~')
    
    # Remove proxy settings from shell rc files
    for rc_file in ['.zshrc', '.bashrc', '.profile']:
        rc_path = os.path.join(actual_home, rc_file)
        if os.path.exists(rc_path):
            try:
                with open(rc_path, 'r') as f:
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
                    if 'proxy_on' in line or 'proxy_off' in line or 'proxy_status' in line:
                        continue
                    if 'http_proxy' in line or 'https_proxy' in line or 'all_proxy' in line:
                        continue
                    new_lines.append(line)
                
                # Write back cleaned content
                with open(rc_path, 'w') as f:
                    f.writelines(new_lines)
                
                log(f"Removed proxy settings from ~/{rc_file}", "SUCCESS")
            except Exception as e:
                log(f"Failed to clean ~/{rc_file}: {str(e)}", "WARNING")
    
    # Reset ProxyChains to default if backup exists
    if os.path.exists(f"{CONFIG.PROXYCHAINS_CONFIG}.backup"):
        try:
            shutil.copy(f"{CONFIG.PROXYCHAINS_CONFIG}.backup", CONFIG.PROXYCHAINS_CONFIG)
            proxychains_name = "proxychains-ng" if IS_MACOS else "ProxyChains4"
            log(f"Restored {proxychains_name} to default configuration", "SUCCESS")
        except Exception as e:
            log(f"Failed to restore ProxyChains: {str(e)}", "WARNING")
    
    print("\n" + "="*60)
    print(f"{Colors.GREEN}✓ System proxy has been reset to default{Colors.END}")
    print("="*60)
    print("\nChanges made:")
    print("  1. V2Ray service stopped and disabled")
    print("  2. Removed proxy settings from shell configuration files")
    print("  3. Restored ProxyChains to default (if backup exists)")
    print("\nNote: You need to restart your terminal or run 'source ~/.zshrc'")
    print("      for the changes to take effect in current session.")

def show_help():
    """Display help information"""
    help_text = f"""
{Colors.HEADER}================================================================================
                    V2Ray Cross-Platform Management Tool - Help
================================================================================{Colors.END}

[Platform Support]
  • macOS (10.12+)
  • Linux (Ubuntu/Debian/CentOS/Fedora)
  • Full feature parity across platforms

[Features]
  • Complete V2Ray installation and deployment
  • Support subscription parsing (vmess/vless protocols)
  • 24 built-in backup nodes
  • Advanced latency testing
  • System proxy configuration
  • Cross-platform service management
  • Configuration backup and restore
  • Detailed logging

[Main Functions]

1. {Colors.BOLD}Quick Start{Colors.END}
   - One-click setup wizard for new users
   - Automatic platform detection
   - Guided configuration

2. {Colors.BOLD}Node Management{Colors.END}
   - Switch nodes
   - Test current node
   - Test all nodes

3. {Colors.BOLD}Subscription Management{Colors.END}
   - Add/update subscription
   - Automatic parsing

4. {Colors.BOLD}System Configuration{Colors.END}
   - Configure system proxy
   - Platform-specific optimizations

[Configuration Locations]
  macOS:
    - V2Ray: /usr/local/etc/v2ray/config.json
    - Logs: /usr/local/var/log/v2ray_command.log
    - Service: /Library/LaunchDaemons/com.v2ray.core.plist

  Linux:
    - V2Ray: /etc/v2ray/config.json
    - Logs: /var/log/v2ray_command.log
    - Service: /etc/systemd/system/v2ray.service

[Proxy Ports]
  - SOCKS5: 127.0.0.1:10808
  - HTTP: 127.0.0.1:10809

================================================================================
"""
    print(help_text)

def show_status():
    """Display current status"""
    print(f"\n{Colors.HEADER}V2Ray Service Status{Colors.END}")
    print("="*60)
    
    # Platform info
    print(f"Platform: {Colors.CYAN}{platform.system()} {platform.release()}{Colors.END}")
    
    # Service status
    if PLATFORM_HANDLER.is_service_active():
        print(f"Service Status: {Colors.GREEN}Running{Colors.END}")
    else:
        print(f"Service Status: {Colors.RED}Stopped{Colors.END}")
    
    # Current node
    print(f"Current Node: {Colors.BOLD}{Colors.CYAN}{get_current_node_info()}{Colors.END}")
    
    # IP information
    if PLATFORM_HANDLER.is_service_active():
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

def show_main_menu():
    """Display main menu"""
    print(f"\n{Colors.BOLD}V2Ray Cross-Platform Management Tool v3.0{Colors.END}")
    print(f"Platform: {Colors.CYAN}{platform.system()}{Colors.END}")
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
    print("   42. Sync ProxyChains")
    print("   43. Reset System Proxy to Default")
    print("5. Advanced Features")
    print("   51. View Service Status")
    print("   52. Test Proxy Connection")
    print("   53. Restore Configuration Backup")
    print("   54. View Logs")
    print("6. Help")
    print("0. Exit")
    print("="*60)

def main():
    """Main function"""
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--help", "-h"]:
            show_help()
            return 0
    
    # Enter interactive menu
    print(f"{Colors.HEADER}V2Ray Cross-Platform Management Tool{Colors.END}")
    print(f"Version: 3.0.0 | Platform: {platform.system()}\n")
    
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
                    with open(CONFIG.CONFIG_FILE, 'r') as f:
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
                # Sync ProxyChains
                PLATFORM_HANDLER.configure_proxychains()
                log("ProxyChains configuration synchronized", "SUCCESS")
            
            elif choice == "43":
                # Reset system proxy to default
                confirm = input("\nAre you sure you want to reset system proxy to default? This will:\n"
                              "- Stop and disable V2Ray service\n"
                              "- Remove all proxy settings from shell configuration\n"
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
                if os.path.exists(CONFIG.LOG_FILE):
                    run_command(f"tail -n 50 {CONFIG.LOG_FILE}", capture_output=False)
                else:
                    log("Log file does not exist", "WARNING")
            
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