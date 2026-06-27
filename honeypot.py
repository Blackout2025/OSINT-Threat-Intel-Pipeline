import socket
import sys
import threading
import datetime
import hashlib
import urllib.request
import json
import re
import time
import paramiko

# ==========================================
# 1. CONFIGURATION INTERFACE & KEYS
# ==========================================
BIND_IP = "0.0.0.0"
BIND_PORT = 2222
LOG_FILE = "honeypot_security.log"

try:
    HOST_KEY = paramiko.RSAKey(filename='server.key')
except Exception as e:
    print(f"[-] Key Error: Missing 'server.key' file! Run keygen first. Details: {e}")
    sys.exit(1)

# ==========================================
# 2. PRIVACY-FIRST COMPLIANCE & INTEL LAYER
# ==========================================
def gdpr_hash_ip(ip_address):
    """Pseudonymizes the source IP address using SHA-256 for GDPR compliance."""
    salt = "DE_SECURITY_AUSBILDUNG_2026"
    hashed = hashlib.sha256((ip_address + salt).encode('utf-8')).hexdigest()
    return hashed[:12]

def locate_attacker_ip(raw_ip):
    """Gathers geolocation metrics to map out incoming global threat vectors."""
    # SIMULATION TWIST: If testing locally, fake a real German server IP to see the API work!
    if raw_ip in ["127.0.0.1", "localhost", "::1"]:
        raw_ip = "78.46.40.1" # Example public IP located in Germany (Hetzner)
        
    try:
        url = f"http://ip-api.com/json/{raw_ip}?fields=status,country,city,isp"
        response = urllib.request.urlopen(url, timeout=3.0)
        data = json.loads(response.read().decode())
        if data.get("status") == "success":
            return f"{data.get('country')}/{data.get('city')} ({data.get('isp')})"
    except Exception:
        pass
    return "UNKNOWN_LOCATION"

def log_event(raw_ip, action, details):
    """Appends audit data to persistent storage safely without raw PII logging."""
    pseudo_id = gdpr_hash_ip(raw_ip)
    location = locate_attacker_ip(raw_ip)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"[{timestamp}] ID:{pseudo_id} | LOC:{location} | ACTION:{action} | DATA:{details}\n"
    print(log_entry.strip())
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

# ==========================================
# 3. SSH INTERFACE HANDSHAKE HANDLING
# ==========================================
class SSHAuthenticationEngine(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        log_event(self.client_ip, "CRED_CAPTURE", f"USER: '{username}' | PASS: '{password}'")
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

# ==========================================
# 4. HIGH-FIDELITY CHARACTER-ECHO SHELL ENGINE
# ==========================================
def execute_interactive_sandbox(channel, username, client_ip):
    """Manages character echoing and command tracking parameters within the PTY."""
    channel.send("Welcome to Ubuntu 22.04.2 LTS (GNU/Linux 5.15.0-generic x86_64)\r\n\r\n")

    while True:
        prompt = f"root@server1:~# "
        channel.send(prompt)
        
        buffer = ""
        while True:
            char = channel.recv(1).decode('utf-8', errors='ignore')
            if not char:
                break
            
            if char != '\r' and char != '\n':
                channel.send(char)
                buffer += char
            elif char == '\r':
                channel.send("\r\n")
                break
        
        command_clean = buffer.strip()
        if command_clean == "":
            continue

        log_event(client_ip, "CMD_EXEC", f"COMMAND: '{command_clean}'")

        # MASTER COMMAND EVALUATION ROUTING BOARD
        if command_clean in ["exit", "logout"]:
            channel.send("logout\r\nConnection to localhost closed.\r\n")
            break
            
        elif command_clean == "ls":
            channel.send("bin  boot  dev  etc  home  lib  root  sys  usr  var\r\n")
            
        elif command_clean == "ls -la" or command_clean == "ls-la":
            ls_la_output = (
                "total 64\r\n"
                "drwxr-xr-x  20 root root 4096 Jun 27 05:00 .\r\n"
                "drwxr-xr-x  20 root root 4096 Jun 27 05:00 ..\r\n"
                "drwxr-xr-x   2 root root 4096 May 12 11:15 bin\r\n"
                "drwxr-xr-x   4 root root 4096 Jun 01 09:22 etc\r\n"
                "drwxr-xr-x   2 root root 4096 Apr 18 14:40 root\r\n"
            )
            channel.send(ls_la_output)
            
        elif command_clean == "whoami":
            channel.send("root\r\n")
            
        elif command_clean == "uname -a":
            channel.send("Linux server1 5.15.0-generic #74-Ubuntu SMP x86_64 GNU/Linux\r\n")
            
        elif "wget" in command_clean or "curl" in command_clean:
            url_extractor = re.findall(r'(https?://[^\s|]+)', command_clean)
            extracted_url = url_extractor[0] if url_extractor else "NO_URL_FOUND"
            
            log_event(client_ip, "MALWARE_STAGING", f"BLOB: '{command_clean}' | EXTRACTED_C2: {extracted_url}")
            
            # --- HIGH FIDELITY DOWNLOAD SIMULATION ---
            channel.send(f"Connecting to {extracted_url}... connected.\r\n")
            time.sleep(1.2) # Realistic network connection overhead pause
            channel.send("HTTP request sent, awaiting response... 200 OK\r\n")
            time.sleep(1.0)
            channel.send("Length: 4096 (4K) [text/sh]\r\nSaving to: 'malware.sh'\r\n\r\n")
            
            # Simulate a live loading progress bar sequence
            time.sleep(0.8)
            channel.send("malware.sh            0%[                    ]       0  --.-KB/s")
            time.sleep(1.1)
            channel.send("\rmalware.sh           50%[==========>          ]   2.04K  2.11KB/s")
            time.sleep(0.9)
            channel.send("\rmalware.sh          100%[===================>]   4.00K  4.15KB/s    in 1.5s\r\n\r\n")
            channel.send(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} URL:{extracted_url} [4096/4096] -> \"malware.sh\" saved [4096/4096]\r\n")
            
        else:
            error_msg = f"bash: {command_clean}: command not found\r\n"
            channel.send(error_msg)

# ==========================================
# 5. CORE DAEMON MULTITHREAD ENGINE
# ==========================================
def handle_ssh_attacker(client_socket, remote_address):
    ip, port = remote_address
    log_event(ip, "CONN_ATTEMPT", f"Source Port: {port}")

    try:
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(HOST_KEY)
        
        server_interface = SSHAuthenticationEngine(ip)
        transport.start_server(server=server_interface)

        channel = transport.accept(20)
        if channel is None: return

        server_interface.event.wait(10)
        if not server_interface.event.is_set(): return

        execute_interactive_sandbox(channel, "root", ip)

    except Exception as e:
        log_event(ip, "CONN_ERROR", str(e))
    finally:
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((BIND_IP, BIND_PORT))
    server.listen(10)
    server.settimeout(1.0)
    print(f"[+] Cryptographic SSH Honeypot Active on {BIND_IP}:{BIND_PORT}...")

    while True:
        try:
            client_sock, address = server.accept()
            t = threading.Thread(target=handle_ssh_attacker, args=(client_sock, address))
            t.daemon = True
            t.start()
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            print("\n[-] [SIGINT] Shutting down honeypot engine gracefully. Auf Wiedersehen!")
            break
        except Exception as e:
            print(f"[-] Runtime Exception: {e}")

if __name__ == "__main__":
    start_server()