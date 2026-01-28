import os
import sys
import time
import logging
import socket
import configparser
import subprocess
from logging.handlers import RotatingFileHandler

# Configuration
LOG_FILE = "app.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 9  # 9 backups + 1 current = 10 files total (~100MB)
CHECK_INTERVAL = 60  # 1 minute
WAN_LOGINER_SCRIPT = "WanLoginer.py"
AC_IP = "10.13.7.59"  # From WanLoginer.py

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    # Rotating File Handler
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT, encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

def get_local_ip():
    """
    Detect local IP by connecting to the auth server.
    Copied/Adapted from WanLoginer.py logic.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # connect to the auth server to determine the correct outgoing interface
        s.connect((AC_IP, 19008))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            # Fallback to public DNS
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("223.5.5.5", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

def update_config():
    """
    Read ENV variables and update config.ini
    """
    username = os.environ.get("AUTH_USER")
    password = os.environ.get("AUTH_PASS")
    host_ip = os.environ.get("HOST_IP")

    if not username or not password:
        logger.warning("AUTH_USER or AUTH_PASS not set in environment variables. Assuming config.ini is manually mounted or already valid.")
        return

    target_ip = host_ip
    if not target_ip:
        logger.info("HOST_IP not set. Attempting to detect local IP...")
        target_ip = get_local_ip()
        logger.info(f"Detected IP: {target_ip}")
    else:
        logger.info(f"Using specified HOST_IP: {target_ip}")

    config = configparser.ConfigParser()
    config.read('config.ini')
    
    if not config.has_section('UserConfig'):
        config.add_section('UserConfig')
    
    config.set('UserConfig', 'username', username)
    config.set('UserConfig', 'password', password)
    config.set('UserConfig', 'u_ip', target_ip)
    
    with open('config.ini', 'w') as config_file:
        config.write(config_file)
    logger.info("config.ini updated successfully.")

def check_internet(host="223.5.5.5"): # Alidns is stable
    try:
        # -c 1 for linux
        subprocess.check_call(['ping', '-c', '1', '-W', '2', host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False
    except Exception as e:
        logger.error(f"Error checking internet: {e}")
        return False

def main():
    logger.info("WanLoginer Docker Entrypoint Started.")
    
    # Update config first
    update_config()
    
    while True:
        try:
            logger.info("Checking network connectivity...")
            if check_internet():
                logger.info("Network is Online.")
            else:
                logger.warning("Network is Offline. Starting authentication...")
                try:
                    # Run WanLoginer.py
                    # We capture output to log it
                    result = subprocess.run(
                        [sys.executable, WAN_LOGINER_SCRIPT],
                        capture_output=True,
                        text=True,
                        check=False 
                    )
                    
                    # Log stdout
                    if result.stdout:
                        for line in result.stdout.splitlines():
                            logger.info(f"[WanLoginer] {line}")
                    
                    # Log stderr
                    if result.stderr:
                        for line in result.stderr.splitlines():
                            logger.error(f"[WanLoginer Error] {line}")
                            
                    if result.returncode == 0:
                        logger.info("WanLoginer finished successfully.")
                    else:
                        logger.error(f"WanLoginer failed with return code {result.returncode}")
                        
                except Exception as e:
                    logger.error(f"Failed to execute WanLoginer.py: {e}")

        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        
        logger.info(f"Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
