#!/bin/bash
# V2Ray Proxy Configuration

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
        echo -n "Direct connection IP: "
        curl -s https://ipinfo.io/ip 2>/dev/null || echo "Unable to fetch"
    else
        echo "Proxy is ON"
        echo "HTTP Proxy: $http_proxy"
        echo "SOCKS Proxy: $all_proxy"
        echo
        echo "Proxy IP Information:"
        echo "===================="

        # 获取 IP 信息
        local ip_info=$(curl -s https://ipinfo.io 2>/dev/null)

        if [ -n "$ip_info" ]; then
            # 使用 Python 或 jq 解析 JSON（如果可用）
            if command -v python3 >/dev/null 2>&1; then
                # 使用 Python 解析 JSON
                echo "$ip_info" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f\"IP Address: {data.get('ip', 'N/A')}\")
    print(f\"Location: {data.get('city', 'N/A')}, {data.get('region', 'N/A')}, {data.get('country', 'N/A')}\")
    print(f\"Coordinates: {data.get('loc', 'N/A')}\")
    print(f\"ISP/Organization: {data.get('org', 'N/A')}\")
    print(f\"Timezone: {data.get('timezone', 'N/A')}\")
except:
    print('Error parsing IP information')
"
            elif command -v jq >/dev/null 2>&1; then
                # 使用 jq 解析 JSON
                echo "IP Address: $(echo "$ip_info" | jq -r .ip)"
                echo "Location: $(echo "$ip_info" | jq -r '"\(.city), \(.region), \(.country)"')"
                echo "Coordinates: $(echo "$ip_info" | jq -r .loc)"
                echo "ISP/Organization: $(echo "$ip_info" | jq -r .org)"
                echo "Timezone: $(echo "$ip_info" | jq -r .timezone)"
            else
                # 使用 grep 作为后备方案
                local ip=$(echo "$ip_info" | grep -oP '"ip":\s*"\K[^"]*' 2>/dev/null || echo "N/A")
                local city=$(echo "$ip_info" | grep -oP '"city":\s*"\K[^"]*' 2>/dev/null || echo "N/A")
                local region=$(echo "$ip_info" | grep -oP '"region":\s*"\K[^"]*' 2>/dev/null || echo "N/A")
                local country=$(echo "$ip_info" | grep -oP '"country":\s*"\K[^"]*' 2>/dev/null || echo "N/A")
                local loc=$(echo "$ip_info" | grep -oP '"loc":\s*"\K[^"]*' 2>/dev/null || echo "N/A")
                local org=$(echo "$ip_info" | grep -oP '"org":\s*"\K[^"]*' 2>/dev/null || echo "N/A")
                local timezone=$(echo "$ip_info" | grep -oP '"timezone":\s*"\K[^"]*' 2>/dev/null || echo "N/A")

                echo "IP Address: $ip"
                echo "Location: $city, $region, $country"
                echo "Coordinates: $loc"
                echo "ISP/Organization: $org"
                echo "Timezone: $timezone"
            fi
        else
            echo "Unable to fetch proxy IP information"
        fi
    fi
}

# V2Ray代理模式管理
proxy_mode_direct() {
    local v2ray_script="$HOME/v2ray_proxy/v2ray_command.py"
    if [ -f "$v2ray_script" ]; then
        sudo python3 "$v2ray_script" mode direct
    else
        echo "错误: 找不到 v2ray_command.py (路径: $v2ray_script)"
    fi
}

proxy_mode_chained() {
    local v2ray_script="$HOME/v2ray_proxy/v2ray_command.py"
    if [ -f "$v2ray_script" ]; then
        sudo python3 "$v2ray_script" mode chained
    else
        echo "错误: 找不到 v2ray_command.py (路径: $v2ray_script)"
    fi
}

proxy_mode_toggle() {
    local v2ray_script="$HOME/v2ray_proxy/v2ray_command.py"
    if [ -f "$v2ray_script" ]; then
        sudo python3 "$v2ray_script" mode toggle
    else
        echo "错误: 找不到 v2ray_command.py (路径: $v2ray_script)"
    fi
}

proxy_mode_status() {
    local v2ray_script="$HOME/v2ray_proxy/v2ray_command.py"
    if [ -f "$v2ray_script" ]; then
        python3 "$v2ray_script" mode status
    else
        echo "错误: 找不到 v2ray_command.py (路径: $v2ray_script)"
    fi
}

proxy_help() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║              V2Ray 代理管理快捷命令                          ║
╚══════════════════════════════════════════════════════════════╝

【环境变量管理】
  proxy_on          - 启用系统代理环境变量
  proxy_off         - 禁用系统代理环境变量
  proxy_status      - 查看代理状态和出口IP信息

【代理模式切换】
  proxy_mode_direct   - 切换到一级代理 (本机 → V2Ray → 互联网)
  proxy_mode_chained  - 切换到二级代理 (本机 → V2Ray → 静态IP → 互联网)
  proxy_mode_toggle   - 一键切换代理模式
  proxy_mode_status   - 查看当前代理模式

【帮助】
  proxy_help        - 显示此帮助信息

╔══════════════════════════════════════════════════════════════╗
║ 使用示例                                                     ║
╚══════════════════════════════════════════════════════════════╝

  # 启用代理环境变量
  $ proxy_on

  # 查看当前IP和代理状态
  $ proxy_status

  # 切换到二级代理（使用静态IP）
  $ proxy_mode_chained

  # 查看当前代理模式
  $ proxy_mode_status

  # 快速切换代理模式
  $ proxy_mode_toggle

  # 禁用代理环境变量
  $ proxy_off

╔══════════════════════════════════════════════════════════════╗
║ 说明                                                         ║
╚══════════════════════════════════════════════════════════════╝

  • 一级代理: 适合日常使用，速度快
  • 二级代理: 通过静态IP访问，适合需要固定IP的场景
  • proxy_on/off 只控制环境变量，不影响V2Ray服务
  • 代理模式切换需要sudo权限，会自动重启V2Ray服务

EOF
}