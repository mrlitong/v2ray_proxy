# V2Ray Proxy Complete Configuration Guide

## Zero. Quick Start

### 🎯 Cross-Platform Support (v3.0+)
This tool now supports both **macOS** and **Linux** with full feature parity!

### For New Users

#### macOS Installation
```bash
# Download the management tool
curl -O https://raw.githubusercontent.com/yourusername/v2ray_proxy/main/v2ray_command.py

# Run quick installation (some operations need sudo)
python3 v2ray_command.py

# Select 1 - Quick Start
```

#### Linux Installation
```bash
# Download the management tool
wget https://raw.githubusercontent.com/yourusername/v2ray_proxy/main/v2ray_command.py

# Run quick installation (requires root privileges)
sudo python3 v2ray_command.py

# Select 1 - Quick Start
```

The management tool will automatically:
- Check system environment and network connection
- Install V2Ray and all necessary dependencies
- Guide you to configure subscription or use built-in nodes
- Test and select the best node
- Configure system proxy

## 1. System Environment Overview

### 1.1 Basic Information
- **Operating Systems**: 
  - macOS 10.12+ (Sierra and later)
  - Ubuntu/Debian Linux
  - Other Linux distributions with systemd
- **V2Ray Version**: V2Ray 5.x (V2Fly Community Edition)
- **Management Tool**: v2ray_command.py v3.0.0 (Cross-platform)
- **Supported Protocols**: VMess/VLESS
- **Permission Requirements**: 
  - Linux: Requires root privileges (sudo)
  - macOS: Some operations require sudo

### 1.2 Core Components

#### Platform-Specific Paths

**macOS:**
| Component | Path/Port | Purpose |
|-----------|-----------|---------|
| V2Ray Main Program | `/usr/local/bin/v2ray` | Proxy service core |
| V2Ray Config | `/usr/local/etc/v2ray/config.json` | Node configuration file |
| Subscription Config | `/usr/local/etc/v2ray/subscription.json` | Subscription node storage |
| Management Script | `v2ray_command.py` | Cross-platform management tool |
| proxychains-ng | `/usr/local/bin/proxychains4` | Force proxy tool |
| proxychains Config | `/usr/local/etc/proxychains-ng.conf` | Proxy chain configuration |
| Service File | `/Library/LaunchDaemons/com.v2ray.core.plist` | launchd service |
| System Log | `/usr/local/var/log/v2ray_command.log` | Operation log record |

**Linux:**
| Component | Path/Port | Purpose |
|-----------|-----------|---------|
| V2Ray Main Program | `/usr/local/bin/v2ray` | Proxy service core |
| V2Ray Config | `/etc/v2ray/config.json` | Node configuration file |
| Subscription Config | `/etc/v2ray/subscription.json` | Subscription node storage |
| Management Script | `v2ray_command.py` | Cross-platform management tool |
| ProxyChains4 | `/usr/bin/proxychains4` | Force proxy tool |
| ProxyChains4 Config | `/etc/proxychains4.conf` | Proxy chain configuration |
| Service File | `/etc/systemd/system/v2ray.service` | systemd service |
| System Log | `/var/log/v2ray_command.log` | Operation log record |

**Common Ports (All Platforms):**
| Port | Protocol | Purpose |
|------|----------|---------|  
| `127.0.0.1:10808` | SOCKS5 | Local SOCKS5 proxy |
| `127.0.0.1:10809` | HTTP | Local HTTP proxy |

### 1.3 System Proxy Configuration
Environment variables configured in `~/.zshrc`:
```bash
export http_proxy="http://127.0.0.1:10809"
export https_proxy="http://127.0.0.1:10809"
export socks_proxy="socks5://127.0.0.1:10808"
export all_proxy="socks5://127.0.0.1:10808"
export no_proxy="localhost,127.0.0.1,localaddress,.localdomain.com"
```

## 2. V2Ray Service Management

### 2.1 Service Control Commands

#### macOS (launchd)
```bash
# Start service
sudo launchctl load /Library/LaunchDaemons/com.v2ray.core.plist

# Stop service
sudo launchctl unload /Library/LaunchDaemons/com.v2ray.core.plist

# Check service status
sudo launchctl list | grep v2ray

# Service auto-starts by default with RunAtLoad=true
```

#### Linux (systemd)
```bash
# Start service
sudo systemctl start v2ray

# Stop service
sudo systemctl stop v2ray

# Restart service
sudo systemctl restart v2ray

# Check service status
sudo systemctl status v2ray

# Enable auto-start on boot
sudo systemctl enable v2ray

# Disable auto-start on boot
sudo systemctl disable v2ray
```

### 2.2 Log Viewing

#### macOS
```bash
# View V2Ray logs
tail -f /usr/local/var/log/v2ray_command.log

# View service output
tail -f /usr/local/var/log/v2ray_command.log.out

# View service errors
tail -f /usr/local/var/log/v2ray_command.log.error
```

#### Linux
```bash
# View logs in real-time
sudo journalctl -u v2ray -f

# View last 100 lines of logs
sudo journalctl -u v2ray -n 100

# View logs for specific time period
sudo journalctl -u v2ray --since "2025-07-16 10:00"

# View management tool logs
tail -f /var/log/v2ray_command.log
```

### 2.3 Configuration Validation

#### macOS
```bash
# Validate configuration file syntax
/usr/local/bin/v2ray test -config /usr/local/etc/v2ray/config.json

# Check port listening status
sudo lsof -i:10808
sudo lsof -i:10809
netstat -an | grep -E "10808|10809"
```

#### Linux
```bash
# Validate configuration file syntax
/usr/local/bin/v2ray test -config /etc/v2ray/config.json

# Check port listening status
sudo netstat -tlnp | grep v2ray
sudo ss -tlnp | grep -E "10808|10809"
```

## 3. V2Ray Comprehensive Management Tool

### 3.1 Quick Installation and Configuration
For new users, the quick start feature is recommended:

**macOS:**
```bash
# Run management tool (some operations require sudo)
python3 v2ray_command.py

# Select 1 - Quick Start
# The tool will automatically:
# - Install Homebrew if not present
# - Install dependencies via brew
# - Configure launchd service
```

**Linux:**
```bash
# Run management tool (requires sudo privileges)
sudo python3 v2ray_command.py

# Select 1 - Quick Start
# The tool will automatically:
# - Update package lists
# - Install dependencies via apt
# - Configure systemd service
```

### 3.2 Subscription Feature Description
The management tool supports two node sources:
1. **Subscription Nodes**: Import via subscription URL, supports VMess/VLESS protocols
2. **Built-in Nodes**: 24 pre-configured nodes as backup options

Subscription Priority:
- If subscription is configured, subscription nodes are prioritized
- If no subscription or subscription fails, built-in nodes are used
- Subscription information is saved in `/etc/v2ray/subscription.json`

### 3.3 Management Tool Feature Details
```bash
# Run comprehensive management tool
sudo python3 v2ray_command.py
```

Main Function Modules:

#### 1. **Quick Start (Recommended for New Users)**
   - One-click V2Ray installation and deployment
   - Automatic system environment check
   - Install necessary dependencies (curl, wget, unzip, jq, proxychains4)
   - Support subscription import or use built-in nodes
   - Automatically test and select best node
   - Configure system proxy environment

#### 2. **Node Management**
   - **Switch Node (21)**: Manually select and switch nodes
     - Display grouped by region
     - Test node latency before switching
     - Automatically backup current configuration
     - Auto-rollback on failure
   - **Test Current Node (22)**: Check current node connection status
   - **Test All Nodes (23)**: Batch test, recommend best node
     - Concurrent testing for efficiency
     - Display latency and success rate
     - Automatically recommend optimal node
     - Auto-filter subscription metadata (traffic/expiry info)

#### 3. **Subscription Management**
   - **Update Subscription (31)**: Get latest nodes from subscription URL
     - Support VMess/VLESS protocols
     - Automatically parse subscription content
     - Count nodes by region
     - Save subscription info for future use

#### 4. **System Configuration**
   - **Configure System Proxy (41)**: Set environment variables and shell functions
     - Automatically configure proxy environment variables
     - Provide proxy_on/proxy_off/proxy_status commands
   - **Sync ProxyChains4 (42)**: Ensure port configuration is correct

#### 5. **Advanced Features**
   - **View Service Status (51)**: Display V2Ray running status and node info
   - **Test Proxy Connection (52)**: Verify SOCKS5 and HTTP proxy
   - **Restore Configuration Backup (53)**: Quickly restore previous configuration
   - **View Logs (54)**: View recent operation logs
   - **Display Proxy Status (55)**: Beautified status display

### 3.4 Command Line Parameters
```bash
# Directly display proxy status (beautified version)
python3 v2ray_command.py proxy_status

# Display help information
python3 v2ray_command.py --help
```

The `proxy_status` command will display:
- V2Ray service status
- Current node information
- Proxy IP address and location
- Terminal proxy configuration status
- Local IP comparison

### 3.5 Built-in Node Distribution
| Region | Node Count | Port Range | Recommended Use |
|--------|------------|------------|-----------------|
| Hong Kong | 8 | 30001-30004, 30020-30023 | Access mainland services |
| Japan | 2 | 30005-30006 | High speed and stable |
| Singapore | 2 | 30007-30008 | Best for local |
| Taiwan | 2 | 30009-30010 | Specific services |
| USA | 4 | 30011-30014 | Access US services |
| Others | 5 | 30015-30019, 30024 | Special needs |

### 3.6 Manual Node Switching
To modify manually, edit the configuration file:
```bash
sudo nano /etc/v2ray/config.json
```

Modify the server address and port in the outbounds section:
```json
{
  "address": "phoenicis.weltknoten.xyz",
  "port": 30005
}
```

Then restart the service:
```bash
sudo systemctl restart v2ray
```

## 4. ProxyChains Usage Guide

### 4.1 Basic Usage
**macOS uses proxychains-ng**, **Linux uses ProxyChains4**. Both work similarly to force programs that don't support proxy to access the network through proxy.

```bash
# Basic format
proxychains4 [program] [parameters]

# Silent mode (recommended)
proxychains4 -q [program] [parameters]
```

### 4.2 Common Examples
```bash
# Git operations
proxychains4 -q git clone https://github.com/user/repo.git
proxychains4 -q git pull

# Package managers
proxychains4 -q pip install package_name
proxychains4 -q npm install package_name
proxychains4 -q cargo install package_name

# Download tools
proxychains4 -q wget https://example.com/file.zip
proxychains4 -q curl https://api.example.com

# Development tools
proxychains4 -q docker pull image:tag
proxychains4 -q kubectl get pods

# Special alias (configured in .zshrc)
ccd  # Equivalent to proxychains4 -q claude --dangerously-skip-permissions
```

### 4.3 ProxyChains Configuration Description

**macOS** (`/usr/local/etc/proxychains-ng.conf`):
- **Proxy Mode**: strict_chain (strict chain, all proxies must be available)
- **DNS Proxy**: Enabled (prevent DNS leak)
- **Proxy Server**: SOCKS5 127.0.0.1:10808

**Linux** (`/etc/proxychains4.conf`):
- **Proxy Mode**: dynamic_chain (flexible chain mode)
- **DNS Proxy**: Enabled (prevent DNS leak)
- **Silent Mode**: Enabled (quiet_mode on)
- **Proxy Server**: SOCKS5 127.0.0.1:10808

**Important Note**: ProxyChains4 configuration file must match V2Ray's SOCKS5 port (10808).

Use script for automatic sync:
```bash
# Run management tool
sudo python3 v2ray_command.py
# Select 42 - Sync ProxyChains4 configuration
```

Or update manually:
```bash
sudo sed -i 's/socks5  127.0.0.1 1080/socks5  127.0.0.1 10808/' /etc/proxychains4.conf
```

## 5. Proxy Testing Methods

### 5.1 Basic Connectivity Test
```bash
# Test SOCKS5 proxy
curl -x socks5h://127.0.0.1:10808 https://ipinfo.io

# Test HTTP proxy
curl -x http://127.0.0.1:10809 https://ipinfo.io

# Test ProxyChains4
proxychains4 -q curl https://ipinfo.io

# Test Google access
curl -x socks5h://127.0.0.1:10808 -I https://www.google.com
```

### 5.2 Speed Test
```bash
# Download speed test
curl -x socks5h://127.0.0.1:10808 -o /dev/null -w "%{speed_download}\n" \
  https://speed.hetzner.de/100MB.bin

# Latency test
curl -x socks5h://127.0.0.1:10808 -o /dev/null -w "%{time_total}\n" \
  https://www.google.com
```

### 5.3 DNS Leak Test
```bash
# Check if DNS goes through proxy
curl -x socks5h://127.0.0.1:10808 https://dnsleaktest.com/api/v1/servers | jq
```

## 6. Application Configuration Examples

### 6.1 Git Configuration
```bash
# Set global proxy
git config --global http.proxy http://127.0.0.1:10809
git config --global https.proxy http://127.0.0.1:10809

# Use proxy only for GitHub
git config --global http.https://github.com.proxy http://127.0.0.1:10809

# Remove proxy
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 6.2 Docker Configuration
Create or edit `~/.docker/config.json`:
```json
{
  "proxies": {
    "default": {
      "httpProxy": "http://127.0.0.1:10809",
      "httpsProxy": "http://127.0.0.1:10809",
      "noProxy": "localhost,127.0.0.1"
    }
  }
}
```

### 6.3 APT Package Manager
```bash
# Create proxy configuration
sudo tee /etc/apt/apt.conf.d/proxy.conf <<EOF
Acquire::http::Proxy "http://127.0.0.1:10809/";
Acquire::https::Proxy "http://127.0.0.1:10809/";
EOF

# Remove proxy configuration
sudo rm /etc/apt/apt.conf.d/proxy.conf
```

### 6.4 Snap Configuration
```bash
# Set proxy
sudo snap set system proxy.http="http://127.0.0.1:10809"
sudo snap set system proxy.https="http://127.0.0.1:10809"

# Remove proxy
sudo snap unset system proxy.http
sudo snap unset system proxy.https
```

## 7. Configuration Backup and Recovery

### 7.1 Backup Mechanism
The management tool automatically backs up configurations:
- V2Ray config backup: `/etc/v2ray/config.json.backup`
- Subscription config backup: `/etc/v2ray/subscription.json.backup`
- ProxyChains4 config backup: `/etc/proxychains4.conf.backup`

### 7.2 Restore Configuration Using Script
```bash
# Run management tool
sudo python3 v2ray_command.py
# Select 53 - Restore configuration backup
```

### 7.3 Manual Recovery Method
```bash
# Restore V2Ray configuration
sudo cp /etc/v2ray/config.json.backup /etc/v2ray/config.json
sudo systemctl restart v2ray

# Restore subscription configuration
cp /etc/v2ray/subscription.json.backup /etc/v2ray/subscription.json
```

### 7.4 Manual Backup Creation
```bash
# Backup current configuration
sudo cp /etc/v2ray/config.json /etc/v2ray/config.json.manual_backup
cp /etc/v2ray/subscription.json /etc/v2ray/subscription.json.manual_backup
```

## 8. Common Problem Solutions

### 8.0 Insufficient Permission Error
```bash
# Error message: This script requires root privileges
# Solution: Run with sudo
sudo python3 v2ray_command.py

# Or switch to root user
sudo su
python3 v2ray_command.py
```

### 8.1 V2Ray Service Cannot Start
```bash
# 1. Check configuration file
/usr/local/bin/v2ray test -config /etc/v2ray/config.json

# 2. View detailed errors
sudo journalctl -xe -u v2ray

# 3. Check port usage
sudo lsof -i:10808
sudo lsof -i:10809

# 4. Check permissions
ls -la /etc/v2ray/config.json
```

### 8.2 Cannot Connect to Proxy
```bash
# 1. Confirm V2Ray running status
sudo systemctl status v2ray

# 2. Test local ports
telnet 127.0.0.1 10808
telnet 127.0.0.1 10809

# 3. Check firewall
sudo ufw status

# 4. Try restarting service
sudo systemctl restart v2ray
```

### 8.3 ProxyChains4 Not Working
```bash
# 1. Check configuration file port
grep "socks" /etc/proxychains4.conf

# 2. Confirm V2Ray SOCKS5 port
ss -tlnp | grep 10808

# 3. Test basic functionality
proxychains4 -q curl -I https://www.google.com
```

### 8.4 Slow Speed or Unstable
1. Use node switching script to try other nodes
2. Prioritize geographically closer nodes (e.g., Singapore local nodes)
3. Avoid peak hours
4. Check local network quality

### 8.5 Configuration File Corrupted
```bash
# 1. Use script to restore backup
sudo python3 v2ray_command.py
# Select 53 - Restore configuration backup

# 2. Check configuration file format
/usr/local/bin/v2ray test -config /etc/v2ray/config.json

# 3. Regenerate configuration
# Use script to select any node to regenerate configuration
```

### 8.6 Node Cannot Connect
```bash
# 1. Use script to test all nodes
sudo python3 v2ray_command.py
# Select 23 - Test all node latency

# 2. Select online nodes with low latency
# 3. Avoid frequent node switching
```

## 9. Best Practice Recommendations

### 9.1 Daily Use
1. **Terminal Proxy**: Automatically configured via `.zshrc`, takes effect in new terminals
2. **Temporary Disable**: Use `unset http_proxy https_proxy all_proxy` to disable temporarily
3. **Force Proxy**: Use `proxychains4 -q` for programs that don't recognize environment variables
4. **Quick Status Check**: Use `python3 v2ray_command.py proxy_status` for beautified status view
5. **Proxy Control**: Use `proxy_on`/`proxy_off`/`proxy_status` shortcut commands

### 9.2 Performance Optimization
1. **Node Selection**:
   - Singapore Local: Prioritize Singapore nodes
   - Access China Services: Use Hong Kong nodes
   - Access Japan/Korea Services: Use Japan/Korea nodes
   - Access Europe/US Services: Use US nodes

2. **Regular Maintenance**:
   - Test different node performance weekly
   - Clean logs regularly: `sudo journalctl --vacuum-time=7d`
   - Monitor traffic usage
   - Avoid peak hours during testing, reduce concurrent test frequency

### 9.3 Security Recommendations
1. Don't access banking and other sensitive services through proxy
2. Regularly check configuration file permissions
3. Avoid sharing subscription links and user IDs in public
4. Use HTTPS to ensure end-to-end encryption
5. Regularly backup important configurations

### 9.4 Stability Assurance
1. **Avoid Frequent Switching**: Don't change frequently after selecting a stable node
2. **Regular Testing**: Run node test once a week to understand node status
3. **Keep Backups**: Don't delete auto-generated backup files
4. **Record Stable Nodes**: Remember 2-3 stable available nodes

## 10. Quick Reference Card

### Common Commands Quick Reference
```bash
# V2Ray Management
sudo systemctl start/stop/restart/status v2ray

# Comprehensive Management Tool
sudo python3 v2ray_command.py

# Quick View Proxy Status
python3 v2ray_command.py proxy_status

# Proxy Testing
curl -x socks5h://127.0.0.1:10808 https://ipinfo.io

# Force Proxy
proxychains4 -q [command]

# View V2Ray Logs
sudo journalctl -u v2ray -f

# View Management Tool Logs
tail -f /var/log/v2ray_command.log
```

### Port Information
- SOCKS5: `127.0.0.1:10808`
- HTTP: `127.0.0.1:10809`
- V2Ray Remote: See node list

---
Document Update Time: 2025-08-20
Author: Claude Assistant

### Update Log
- 2025-08-31: **v3.0.0 Major Update - Full Cross-Platform Support**
  - Added complete macOS support (10.12+)
  - Refactored with platform abstraction layer
  - Support for Homebrew package manager on macOS
  - launchd service management for macOS
  - proxychains-ng support for macOS
  - Maintained full backward compatibility with Linux
  - Unified user experience across platforms
- 2025-08-20: Fixed issue with subscription metadata appearing in node tests
- 2025-08-20: Added automatic filtering for non-VPN entries (traffic/expiry info)
- 2025-07-17: Comprehensive update to v2ray_command.py v2.1.0 management tool
- 2025-07-17: Added quick start feature and one-click installation deployment instructions
- 2025-07-17: Added subscription management feature description (supports VMess/VLESS)
- 2025-07-17: Added beautified proxy status display and command line parameter support
- 2025-07-17: Updated all script paths and menu option numbers
- 2025-07-16: Added configuration backup and recovery feature description
- 2025-07-16: Updated ProxyChains4 port configuration to 10808
- 2025-07-16: Added troubleshooting method for configuration file corruption
- 2025-07-16: Enhanced node switching script stability description