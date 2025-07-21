# V2Ray Proxy Status Display Feature Documentation

## Feature Overview

V2Ray proxy status display feature supports two display modes:

### 1. Single Display Mode (Auto Exit)
- Displays proxy status information once and then exits automatically
- Suitable for quickly checking current status

### 2. Real-time Monitoring Mode (3s Refresh)
- Automatically refreshes status information every 3 seconds
- Suitable for continuous proxy status monitoring
- Press Ctrl+C to exit monitoring

#### Optimized Features
- **Smooth Refresh**: Collects all data in the background first (latency test, IP query, etc.), then refreshes display at once
- **Fluid Experience**: Avoids interface flickering and stuttering caused by progressive display
- **Complete Data**: Each refresh displays complete status information

## Usage

### Method 1: Command Line Parameters

```bash
# Single display mode
sudo python3 v2ray_command.py proxy_status

# Real-time monitoring mode
sudo python3 v2ray_command.py proxy_status_refresh
```

### Method 2: Interactive Menu

```bash
sudo python3 v2ray_command.py
```

Then select:
- Option 55: Show Proxy Status (beautified) - Single display
- Option 56: Real-time Monitor Proxy Status (3s refresh)

## Display Content

Status information includes:
- Running time
- V2Ray service status
- Current node information
- Node latency test
- Terminal proxy configuration
- Proxy IP information
- Local IP information

## Notes

1. Requires root privileges to run
2. In real-time monitoring mode, press Ctrl+C to exit
3. Ensure V2Ray service is running to display complete information