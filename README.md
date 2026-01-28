# ShanghaitechLoginer

### EgateLoginer
> modified from https://github.com/Lyutoon/ShanghaiTech/blob/main/login.py

#### Requirements
1. pip install pycryptodome
2. cd Your Python Environment\lib\site-packages， rename the "crypto" folder as "Crypto".

### WanLoginer
#### Requirements
1. opencv-python
2. ddddocr
3. BeautifulSoup

## Quick Start
You can download the pre-built Docker image (`wanloginer.tar`) from the Releases page.

### 1. Load Image
```bash
docker load -i wanloginer.tar
```

### 2. Run Container
```bash
docker run -d \
  --name wanloginer \
  --restart always \
  --network host \
  -e AUTH_USER="your_username" \
  -e AUTH_PASS="your_password" \
  wanloginer
```

### Docker Usage (Build from Source)

This project now supports Docker deployment with auto-reconnection and log management features.

#### 1. Build Image
```bash
docker build -t wanloginer .
```

#### 2. Run Container

**Option A: Host Network (Recommended)**
Use host network mode for accurate local IP detection.
```bash
docker run -d \
  --name wanloginer \
  --restart always \
  --network host \
  -e AUTH_USER="your_username" \
  -e AUTH_PASS="your_password" \
  wanloginer
```

**Option B: Bridge Network (with Manual IP)**
If you cannot use host network, specify the host IP manually.
```bash
docker run -d \
  --name wanloginer \
  --restart always \
  -e AUTH_USER="your_username" \
  -e AUTH_PASS="your_password" \
  -e HOST_IP="192.168.1.100" \
  wanloginer
```

#### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `AUTH_USER` | Your ShanghaiTech username | Yes |
| `AUTH_PASS` | Your ShanghaiTech password | Yes |
| `HOST_IP` | Manually specify the IP address to authenticate. If not set, it attempts to auto-detect the local IP. | No |

#### Features
- **Auto-Reconnect**: Checks internet connectivity every minute and re-authenticates if offline.
- **Smart IP Detection**: Automatically detects the correct local IP for authentication.
- **Log Rotation**: Logs are saved to `app.log` inside the container with a max size of 100MB (10MB x 10 files).
