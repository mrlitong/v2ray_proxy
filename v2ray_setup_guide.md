# V2Ray 代理完整配置指南

## 零、快速开始

### 对于新用户
如果您是第一次安装V2Ray，只需执行以下命令：
```bash
# 下载管理工具（如果还没有）
wget https://raw.githubusercontent.com/yourusername/v2ray_proxy/main/v2ray_command.py

# 运行快速安装（需要root权限）
sudo python3 v2ray_command.py

# 选择 1 - 快速开始
```

管理工具将自动：
- 检查系统环境和网络连接
- 安装V2Ray和所有必要依赖
- 引导您配置订阅或使用内置节点
- 测试并选择最佳节点
- 配置系统代理

## 一、系统环境概览

### 1.1 基础信息
- **操作系统**: Ubuntu/Debian Linux
- **V2Ray 版本**: V2Ray 5.x (V2Fly 社区版)
- **管理工具**: v2ray_command.py v2.1.0
- **支持协议**: VMess/VLESS
- **权限要求**: 需要 root 权限运行管理工具

### 1.2 核心组件
| 组件 | 路径/端口 | 用途 |
|-----|---------|------|
| V2Ray 主程序 | `/usr/local/bin/v2ray` | 代理服务核心 |
| V2Ray 配置 | `/etc/v2ray/config.json` | 节点配置文件 |
| 订阅配置 | `/etc/v2ray/subscription.json` | 订阅节点存储 |
| 管理脚本 | `v2ray_command.py` | 综合管理工具 |
| ProxyChains4 | `/usr/bin/proxychains4` | 强制代理工具 |
| ProxyChains4 配置 | `/etc/proxychains4.conf` | 代理链配置 |
| SOCKS5 代理 | `127.0.0.1:10808` | 本地 SOCKS5 端口 |
| HTTP 代理 | `127.0.0.1:10809` | 本地 HTTP 端口 |
| 系统日志 | `/var/log/v2ray_command.log` | 操作日志记录 |

### 1.3 系统代理配置
在 `~/.zshrc` 中已配置的环境变量：
```bash
export http_proxy="http://127.0.0.1:10809"
export https_proxy="http://127.0.0.1:10809"
export socks_proxy="socks5://127.0.0.1:10808"
export all_proxy="socks5://127.0.0.1:10808"
export no_proxy="localhost,127.0.0.1,localaddress,.localdomain.com"
```

## 二、V2Ray 服务管理

### 2.1 服务控制命令
```bash
# 启动服务
sudo systemctl start v2ray

# 停止服务
sudo systemctl stop v2ray

# 重启服务
sudo systemctl restart v2ray

# 查看服务状态
sudo systemctl status v2ray

# 设置开机自启
sudo systemctl enable v2ray

# 取消开机自启
sudo systemctl disable v2ray
```

### 2.2 日志查看
```bash
# 实时查看日志
sudo journalctl -u v2ray -f

# 查看最近100行日志
sudo journalctl -u v2ray -n 100

# 查看特定时间段的日志
sudo journalctl -u v2ray --since "2025-07-16 10:00"
```

### 2.3 配置验证
```bash
# 验证配置文件语法
/usr/local/bin/v2ray test -config /etc/v2ray/config.json

# 检查端口监听状态
sudo netstat -tlnp | grep v2ray
sudo ss -tlnp | grep -E "10808|10809"
```

## 三、V2Ray 综合管理工具

### 3.1 快速安装和配置
对于新用户，推荐使用快速开始功能：
```bash
# 运行管理工具（需要sudo权限）
sudo python3 v2ray_command.py

# 选择 1 - 快速开始
```

### 3.2 订阅功能说明
管理工具支持两种节点来源：
1. **订阅节点**：通过订阅地址导入，支持VMess/VLESS协议
2. **内置节点**：24个预配置节点，作为备用选择

订阅优先级：
- 如果已配置订阅，优先使用订阅节点
- 如果没有订阅或订阅失败，使用内置节点
- 订阅信息保存在 `/etc/v2ray/subscription.json`

### 3.3 管理工具功能详解
```bash
# 运行综合管理工具
sudo python3 v2ray_command.py
```

主要功能模块：

#### 1. **快速开始（推荐新用户）**
   - 一键完成V2Ray安装部署
   - 自动检查系统环境
   - 安装必要依赖（curl、wget、unzip、jq、proxychains4）
   - 支持订阅导入或使用内置节点
   - 自动测试并选择最佳节点
   - 配置系统代理环境

#### 2. **节点管理**
   - **切换节点（21）**: 手动选择并切换节点
     - 按地区分组显示
     - 切换前测试节点延迟
     - 自动备份当前配置
     - 失败时自动回滚
   - **测试当前节点（22）**: 检测当前节点连接状态
   - **测试所有节点（23）**: 批量测试，推荐最佳节点
     - 并发测试提高效率
     - 显示延迟和成功率
     - 自动推荐最优节点

#### 3. **订阅管理**
   - **更新订阅（31）**: 从订阅地址获取最新节点
     - 支持VMess/VLESS协议
     - 自动解析订阅内容
     - 按地区统计节点数量
     - 保存订阅信息供后续使用

#### 4. **系统配置**
   - **配置系统代理（41）**: 设置环境变量和shell函数
     - 自动配置代理环境变量
     - 提供proxy_on/proxy_off/proxy_status命令
   - **同步ProxyChains4（42）**: 确保端口配置正确

#### 5. **高级功能**
   - **查看服务状态（51）**: 显示V2Ray运行状态和节点信息
   - **测试代理连接（52）**: 验证SOCKS5和HTTP代理
   - **恢复配置备份（53）**: 快速恢复之前的配置
   - **查看日志（54）**: 查看最近的操作日志
   - **显示代理状态（55）**: 美化版状态显示

### 3.4 命令行参数
```bash
# 直接显示代理状态（美化版）
python3 v2ray_command.py proxy_status

# 显示帮助信息
python3 v2ray_command.py --help
```

`proxy_status`命令会显示：
- V2Ray服务状态
- 当前节点信息
- 代理IP地址和位置
- 终端代理配置状态
- 本地IP对比

### 3.5 内置节点分布
| 地区 | 节点数量 | 端口范围 | 推荐用途 |
|-----|---------|---------|---------|
| 香港 | 8个 | 30001-30004, 30020-30023 | 访问内地服务 |
| 日本 | 2个 | 30005-30006 | 高速稳定 |
| 新加坡 | 2个 | 30007-30008 | 本地最佳 |
| 台湾 | 2个 | 30009-30010 | 特定服务 |
| 美国 | 4个 | 30011-30014 | 访问美国服务 |
| 其他 | 5个 | 30015-30019, 30024 | 特殊需求 |

### 3.6 手动切换节点
如需手动修改，编辑配置文件：
```bash
sudo nano /etc/v2ray/config.json
```

修改 outbounds 部分的服务器地址和端口：
```json
{
  "address": "phoenicis.weltknoten.xyz",
  "port": 30005
}
```

然后重启服务：
```bash
sudo systemctl restart v2ray
```

## 四、ProxyChains4 使用指南

### 4.1 基本用法
ProxyChains4 用于强制不支持代理的程序通过代理访问网络。

```bash
# 基本格式
proxychains4 [程序] [参数]

# 静默模式（推荐）
proxychains4 -q [程序] [参数]
```

### 4.2 常用示例
```bash
# Git 操作
proxychains4 -q git clone https://github.com/user/repo.git
proxychains4 -q git pull

# 包管理器
proxychains4 -q pip install package_name
proxychains4 -q npm install package_name
proxychains4 -q cargo install package_name

# 下载工具
proxychains4 -q wget https://example.com/file.zip
proxychains4 -q curl https://api.example.com

# 开发工具
proxychains4 -q docker pull image:tag
proxychains4 -q kubectl get pods

# 特殊别名（已在 .zshrc 中配置）
ccd  # 等同于 proxychains4 -q claude --dangerously-skip-permissions
```

### 4.3 ProxyChains4 配置说明
当前配置（`/etc/proxychains4.conf`）：
- **代理模式**: strict_chain（严格链式，所有代理必须可用）
- **DNS代理**: 启用（防止 DNS 泄漏）
- **静默模式**: 启用（quiet_mode on）
- **代理服务器**: SOCKS5 127.0.0.1:10808

**重要提示**：ProxyChains4 配置文件必须与 V2Ray 的 SOCKS5 端口一致（10808）。

使用脚本自动同步：
```bash
# 运行管理工具
sudo python3 v2ray_command.py
# 选择 42 - 同步 ProxyChains4 配置
```

或手动更新：
```bash
sudo sed -i 's/socks5  127.0.0.1 1080/socks5  127.0.0.1 10808/' /etc/proxychains4.conf
```

## 五、代理测试方法

### 5.1 基础连通性测试
```bash
# 测试 SOCKS5 代理
curl -x socks5h://127.0.0.1:10808 https://ipinfo.io

# 测试 HTTP 代理
curl -x http://127.0.0.1:10809 https://ipinfo.io

# 测试 ProxyChains4
proxychains4 -q curl https://ipinfo.io

# 测试 Google 访问
curl -x socks5h://127.0.0.1:10808 -I https://www.google.com
```

### 5.2 速度测试
```bash
# 下载速度测试
curl -x socks5h://127.0.0.1:10808 -o /dev/null -w "%{speed_download}\n" \
  https://speed.hetzner.de/100MB.bin

# 延迟测试
curl -x socks5h://127.0.0.1:10808 -o /dev/null -w "%{time_total}\n" \
  https://www.google.com
```

### 5.3 DNS 泄漏测试
```bash
# 检查 DNS 是否通过代理
curl -x socks5h://127.0.0.1:10808 https://dnsleaktest.com/api/v1/servers | jq
```

## 六、应用配置示例

### 6.1 Git 配置
```bash
# 设置全局代理
git config --global http.proxy http://127.0.0.1:10809
git config --global https.proxy http://127.0.0.1:10809

# 仅对 GitHub 使用代理
git config --global http.https://github.com.proxy http://127.0.0.1:10809

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 6.2 Docker 配置
创建或编辑 `~/.docker/config.json`：
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

### 6.3 APT 包管理器
```bash
# 创建代理配置
sudo tee /etc/apt/apt.conf.d/proxy.conf <<EOF
Acquire::http::Proxy "http://127.0.0.1:10809/";
Acquire::https::Proxy "http://127.0.0.1:10809/";
EOF

# 删除代理配置
sudo rm /etc/apt/apt.conf.d/proxy.conf
```

### 6.4 Snap 配置
```bash
# 设置代理
sudo snap set system proxy.http="http://127.0.0.1:10809"
sudo snap set system proxy.https="http://127.0.0.1:10809"

# 取消代理
sudo snap unset system proxy.http
sudo snap unset system proxy.https
```

## 七、配置备份与恢复

### 7.1 备份机制
管理工具会自动备份配置：
- V2Ray 配置备份：`/etc/v2ray/config.json.backup`
- 订阅配置备份：`/etc/v2ray/subscription.json.backup`
- ProxyChains4 配置备份：`/etc/proxychains4.conf.backup`

### 7.2 使用脚本恢复配置
```bash
# 运行管理工具
sudo python3 v2ray_command.py
# 选择 53 - 恢复配置备份
```

### 7.3 手动恢复方法
```bash
# 恢复 V2Ray 配置
sudo cp /etc/v2ray/config.json.backup /etc/v2ray/config.json
sudo systemctl restart v2ray

# 恢复订阅配置
cp /etc/v2ray/subscription.json.backup /etc/v2ray/subscription.json
```

### 7.4 手动创建备份
```bash
# 备份当前配置
sudo cp /etc/v2ray/config.json /etc/v2ray/config.json.manual_backup
cp /etc/v2ray/subscription.json /etc/v2ray/subscription.json.manual_backup
```

## 八、常见问题解决

### 8.0 权限不足错误
```bash
# 错误提示：需要 root 权限运行此脚本
# 解决方法：使用 sudo 运行
sudo python3 v2ray_command.py

# 或切换到 root 用户
sudo su
python3 v2ray_command.py
```

### 8.1 V2Ray 服务无法启动
```bash
# 1. 检查配置文件
/usr/local/bin/v2ray test -config /etc/v2ray/config.json

# 2. 查看详细错误
sudo journalctl -xe -u v2ray

# 3. 检查端口占用
sudo lsof -i:10808
sudo lsof -i:10809

# 4. 检查权限
ls -la /etc/v2ray/config.json
```

### 8.2 无法连接到代理
```bash
# 1. 确认 V2Ray 运行状态
sudo systemctl status v2ray

# 2. 测试本地端口
telnet 127.0.0.1 10808
telnet 127.0.0.1 10809

# 3. 检查防火墙
sudo ufw status

# 4. 尝试重启服务
sudo systemctl restart v2ray
```

### 8.3 ProxyChains4 不工作
```bash
# 1. 检查配置文件端口
grep "socks" /etc/proxychains4.conf

# 2. 确认 V2Ray SOCKS5 端口
ss -tlnp | grep 10808

# 3. 测试基本功能
proxychains4 -q curl -I https://www.google.com
```

### 8.4 速度慢或不稳定
1. 使用节点切换脚本尝试其他节点
2. 优先选择地理位置近的节点（如新加坡本地节点）
3. 避开高峰时段
4. 检查本地网络质量

### 8.5 配置文件损坏
```bash
# 1. 使用脚本恢复备份
sudo python3 v2ray_command.py
# 选择 53 - 恢复配置备份

# 2. 检查配置文件格式
/usr/local/bin/v2ray test -config /etc/v2ray/config.json

# 3. 重新生成配置
# 使用脚本选择任意节点重新生成配置
```

### 8.6 节点无法连接
```bash
# 1. 使用脚本测试所有节点
sudo python3 v2ray_command.py
# 选择 23 - 测试所有节点延迟

# 2. 选择延迟低的在线节点
# 3. 避免频繁切换节点
```

## 九、最佳实践建议

### 9.1 日常使用
1. **终端代理**：已通过 `.zshrc` 自动配置，新终端自动生效
2. **临时禁用**：使用 `unset http_proxy https_proxy all_proxy` 临时禁用
3. **强制代理**：对不识别环境变量的程序使用 `proxychains4 -q`
4. **快速状态检查**：使用 `python3 v2ray_command.py proxy_status` 查看美化版状态
5. **代理控制**：使用 `proxy_on`/`proxy_off`/`proxy_status` 快捷命令

### 9.2 性能优化
1. **节点选择**：
   - 新加坡本地：优先使用新加坡节点
   - 访问中国服务：使用香港节点
   - 访问日韩服务：使用日本/韩国节点
   - 访问欧美服务：使用美国节点

2. **定期维护**：
   - 每周测试不同节点性能
   - 定期清理日志：`sudo journalctl --vacuum-time=7d`
   - 监控流量使用情况
   - 测试时避免高峰时段，减少并发测试次数

### 9.3 安全建议
1. 不在代理环境下访问银行等敏感服务
2. 定期检查配置文件权限
3. 避免在公共场合分享订阅链接和用户 ID
4. 使用 HTTPS 确保端到端加密
5. 定期备份重要配置

### 9.4 稳定性保障
1. **避免频繁切换**：选择稳定节点后不要频繁更换
2. **定期测试**：每周运行一次节点测试，了解节点状态
3. **保留备份**：不要删除自动生成的备份文件
4. **记录稳定节点**：记住 2-3 个稳定可用的节点

## 十、快速参考卡片

### 常用命令速查
```bash
# V2Ray 管理
sudo systemctl start/stop/restart/status v2ray

# 综合管理工具
sudo python3 v2ray_command.py

# 快速查看代理状态
python3 v2ray_command.py proxy_status

# 代理测试
curl -x socks5h://127.0.0.1:10808 https://ipinfo.io

# 强制代理
proxychains4 -q [命令]

# 查看V2Ray日志
sudo journalctl -u v2ray -f

# 查看管理工具日志
tail -f /var/log/v2ray_command.log
```

### 端口信息
- SOCKS5: `127.0.0.1:10808`
- HTTP: `127.0.0.1:10809`
- V2Ray 远程: 见节点列表

---
文档更新时间: 2025-07-17
作者: Claude Assistant

### 更新日志
- 2025-07-17: 全面更新为 v2ray_command.py v2.1.0 综合管理工具
- 2025-07-17: 增加快速开始功能和一键安装部署说明
- 2025-07-17: 增加订阅管理功能说明（支持VMess/VLESS）
- 2025-07-17: 增加美化版代理状态显示和命令行参数支持
- 2025-07-17: 更新所有脚本路径和菜单选项编号
- 2025-07-16: 添加配置备份与恢复功能说明
- 2025-07-16: 更新 ProxyChains4 端口配置为 10808
- 2025-07-16: 增加配置文件损坏的故障排除方法
- 2025-07-16: 增强节点切换脚本的稳定性说明