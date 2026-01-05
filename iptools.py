import os
import socket
import subprocess
import platform
import threading
import sys

# ---------------- UTILS ----------------

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def get_local_subnet():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ".".join(ip.split(".")[:3])
    except Exception:
        # Fallback if auto-detection fails
        return None

def ping(ip):
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        result = subprocess.run(
            ["ping", param, "1", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except:
        return False

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Unknown"

# ---------------- DEVICE DISCOVERY ----------------

def discover_hosts():
    subnet = get_local_subnet()

    if not subnet:
        subnet = input("Could not auto-detect subnet.\nEnter subnet (example: 192.168.1): ")

    hosts = []
    threads = []

    def worker(ip):
        if ping(ip):
            hosts.append((ip, get_hostname(ip)))

    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        t = threading.Thread(target=worker, args=(ip,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return hosts

# ---------------- PORT SCAN ----------------

def scan_port(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        open_ = s.connect_ex((ip, port)) == 0
        s.close()
        return open_
    except:
        return False

def scan_port_all_hosts(port):
    clear()
    print(f"Scanning port {port} on all devices...\n")

    hosts = discover_hosts()
    results = []
    threads = []

    def worker(ip, name):
        if scan_port(ip, port):
            results.append((ip, name))

    for ip, name in hosts:
        t = threading.Thread(target=worker, args=(ip, name))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    if not results:
        print("No devices have this port open.")
    else:
        for ip, name in results:
            print(f"{ip:15} | {name} | Port {port} OPEN")

    input("\nPress Enter to continue...")

# ---------------- MENU ----------------

def main():
    try:
        while True:
            clear()
            print("""
██╗██████╗ ████████╗ ██████╗  ██████╗ ██╗     ███████╗
██║██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
██║██████╔╝   ██║   ██║   ██║██║   ██║██║     ███████╗
██║██╔═══╝    ██║   ██║   ██║██║   ██║██║     ╚════██║
██║██║        ██║   ╚██████╔╝╚██████╔╝███████╗███████║
╚═╝╚═╝        ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
            """)
            print("You need to run device discovery before running a port scan. Made by neonroot v1.0")
            print("1) Discover devices")
            print("2) Scan ONE port on ALL devices")
            print("3) Exit\n")

            choice = input("Select option: ")

            if choice == "1":
                clear()
                hosts = discover_hosts()
                for ip, name in hosts:
                    print(f"{ip:15} | {name}")
                input("\nPress Enter...")
            elif choice == "2":
                port = int(input("Port to scan: "))
                scan_port_all_hosts(port)
            elif choice == "3":
                sys.exit(0)

    except Exception as e:
        print("\nFatal error:", e)
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
