#!/bin/bash
# V2Ray Proxy Configuration

# Proxy control functions
proxy_on() {
    export http_proxy="http://127.0.0.1:20809"
    export https_proxy="http://127.0.0.1:20809"
    export HTTP_PROXY="http://127.0.0.1:20809"
    export HTTPS_PROXY="http://127.0.0.1:20809"
    export all_proxy="socks5://127.0.0.1:20808"
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

        # Fetch IP information
        local ip_info=$(curl -s https://ipinfo.io 2>/dev/null)

        if [ -n "$ip_info" ]; then
            # Use Python or jq to parse JSON (if available)
            if command -v python3 >/dev/null 2>&1; then
                # Parse JSON using Python
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
                # Parse JSON using jq
                echo "IP Address: $(echo "$ip_info" | jq -r .ip)"
                echo "Location: $(echo "$ip_info" | jq -r '"\(.city), \(.region), \(.country)"')"
                echo "Coordinates: $(echo "$ip_info" | jq -r .loc)"
                echo "ISP/Organization: $(echo "$ip_info" | jq -r .org)"
                echo "Timezone: $(echo "$ip_info" | jq -r .timezone)"
            else
                # Use grep as fallback
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

# V2Ray Proxy Mode Management
proxy_mode_direct() {
    local v2ray_script="$HOME/v2ray_proxy/v2ray_command.py"
    if [ -f "$v2ray_script" ]; then
        sudo python3 "$v2ray_script" mode direct
    else
        echo "Error: Cannot find v2ray_command.py (path: $v2ray_script)"
    fi
}

proxy_mode_chained() {
    local v2ray_script="$HOME/v2ray_proxy/v2ray_command.py"
    if [ -f "$v2ray_script" ]; then
        sudo python3 "$v2ray_script" mode chained
    else
        echo "Error: Cannot find v2ray_command.py (path: $v2ray_script)"
    fi
}

proxy_mode_toggle() {
    local v2ray_script="$HOME/v2ray_proxy/v2ray_command.py"
    if [ -f "$v2ray_script" ]; then
        sudo python3 "$v2ray_script" mode toggle
    else
        echo "Error: Cannot find v2ray_command.py (path: $v2ray_script)"
    fi
}

proxy_mode_status() {
    local v2ray_script="$HOME/v2ray_proxy/v2ray_command.py"
    if [ -f "$v2ray_script" ]; then
        python3 "$v2ray_script" mode status
    else
        echo "Error: Cannot find v2ray_command.py (path: $v2ray_script)"
    fi
}

proxy_help() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║           V2Ray Proxy Management Quick Commands              ║
╚══════════════════════════════════════════════════════════════╝

【Environment Variable Management】
  proxy_on          - Enable system proxy environment variables
  proxy_off         - Disable system proxy environment variables
  proxy_status      - View proxy status and exit IP information

【Proxy Mode Switching】
  proxy_mode_direct   - Switch to Level-1 Proxy (Local → V2Ray → Internet)
  proxy_mode_chained  - Switch to Level-2 Proxy (Local → V2Ray → Static IP → Internet)
  proxy_mode_toggle   - Quick toggle between proxy modes
  proxy_mode_status   - View current proxy mode

【Help】
  proxy_help        - Display this help information

╔══════════════════════════════════════════════════════════════╗
║ Usage Examples                                               ║
╚══════════════════════════════════════════════════════════════╝

  # Enable proxy environment variables
  $ proxy_on

  # View current IP and proxy status
  $ proxy_status

  # Switch to Level-2 Proxy (using static IP)
  $ proxy_mode_chained

  # View current proxy mode
  $ proxy_mode_status

  # Quick toggle proxy mode
  $ proxy_mode_toggle

  # Disable proxy environment variables
  $ proxy_off

╔══════════════════════════════════════════════════════════════╗
║ Notes                                                        ║
╚══════════════════════════════════════════════════════════════╝

  • Level-1 Proxy: Suitable for daily use, fast speed
  • Level-2 Proxy: Access through static IP, suitable for scenarios requiring fixed IP
  • proxy_on/off only controls environment variables, does not affect V2Ray service
  • Proxy mode switching requires sudo privileges, will automatically restart V2Ray service

EOF
}