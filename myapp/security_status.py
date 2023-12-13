import wmi
import psutil
import subprocess
import time


def get_system_info():
    try:
        # Get CPU usage, RAM usage, and disk usage
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        return cpu_usage, ram_usage, disk_usage
    except Exception as e:
        print(f"Error fetching system information: {e}")
        return None, None, None


def get_network_info():
    try:
        wmi_obj = wmi.WMI()

        # Get MAC Address, IP Address, and Hostname of the primary network adapter (if available)
        network_adapter = wmi_obj.Win32_NetworkAdapterConfiguration(
            IPEnabled=True)
        if network_adapter:
            mac_address = network_adapter[0].MACAddress
            ip_address = network_adapter[0].IPAddress[0] if network_adapter[0].IPAddress else "N/A"
            hostname = wmi_obj.Win32_ComputerSystem()[0].Name
            network_info = psutil.net_io_counters()
            # Convert to Megabytes
            network_usage = (network_info.bytes_sent +
                             network_info.bytes_recv) / (1024 * 1024)
        else:
            mac_address, ip_address, hostname, network_usage = "N/A", "N/A", "N/A", 0

        return mac_address, ip_address, hostname, network_usage
    except Exception as e:
        print(f"Error fetching network information: {e}")
        return None, None, None, None


def is_feature_enabled(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout.strip().lower() == "true"
    except Exception as e:
        return False


def print_info(label, value):
    print(f"{label}: {value}")


while True:
    cpu_usage, ram_usage, disk_usage = get_system_info()
    mac_address, ip_address, hostname, network_usage = get_network_info()

    print_info("CPU Usage", f"{cpu_usage}%")
    print_info("RAM Usage", f"{ram_usage}%")
    print_info("Disk Usage", f"{disk_usage}%")
    print_info("MAC Address", mac_address)
    print_info("IP Address", ip_address)
    print_info("Hostname", hostname)
    print_info("Network Usage", f"{round(network_usage, 2)} MB")

    # Check and print the status of security features
    windows_defender_status = is_feature_enabled(
        ["powershell", "(Get-MpComputerStatus).AntivirusEnabled"])
    windows_firewall_status = is_feature_enabled(
        ["powershell", "(Get-NetFirewallProfile -Name Public).Enabled"])
    windows_auto_updates_status = is_feature_enabled(
        ["sc", "query", "wuauserv"])

    print_info("Windows Defender Antivirus",
               "Enabled" if windows_defender_status else "Disabled")
    print_info("Windows Firewall",
               "Enabled" if windows_firewall_status else "Disabled")
    print_info("Windows Auto-Updates",
               "Enabled" if windows_auto_updates_status else "Disabled")

    print("\n---\n")

    time.sleep(5)
