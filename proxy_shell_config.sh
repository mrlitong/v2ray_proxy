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