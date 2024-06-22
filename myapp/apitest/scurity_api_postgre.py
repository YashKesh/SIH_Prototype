import wmi
import psutil
import subprocess
import time
import psycopg2
import requests

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
        network_adapter = wmi_obj.Win32_NetworkAdapterConfiguration(IPEnabled=True)
        if network_adapter:
            mac_address = network_adapter[0].MACAddress
            ip_address = network_adapter[0].IPAddress[0] if network_adapter[0].IPAddress else "N/A"
            hostname = wmi_obj.Win32_ComputerSystem()[0].Name
            network_info = psutil.net_io_counters()
            # Convert to Megabytes
            network_usage = (network_info.bytes_sent + network_info.bytes_recv) / (1024 * 1024)
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

def send_data_to_postgres(data):
    try:
        # PostgreSQL connection parameters
        postgres_params = {
            'dbname': 'railway',
            'user': 'postgres',
            'password': 'mWxmxUXAsuDTBrCBFRyUWyFdtlzCyQxl',
            'host': 'roundhouse.proxy.rlwy.net',
            'port': '11817'
        }

        # Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(**postgres_params)
        cursor = connection.cursor()

        # Check if the record with the given MAC address already exists
        select_query = "SELECT mac_address FROM myapp_systemstatus WHERE mac_address = %s"
        cursor.execute(select_query, (data["mac_address"],))
        existing_record = cursor.fetchone()

        if existing_record:
            # Update the existing record
            update_query = """
                UPDATE myapp_systemstatus
                SET cpu_usage = %s, ram_usage = %s, disk_usage = %s,
                    ip_address = %s, hostname = %s, network_usage = %s,
                    defender_status = %s, firewall_status = %s,
                    auto_updates_status = %s, timestamp = CURRENT_TIMESTAMP
                WHERE mac_address = %s
            """
            cursor.execute(update_query, (
                data["cpu_usage"], data["ram_usage"], data["disk_usage"],
                data["ip_address"], data["hostname"], data["network_usage"],
                data["defender_status"], data["firewall_status"],
                data["auto_updates_status"], data["mac_address"]
            ))
        else:
            # Insert a new record
            insert_query = """
                INSERT INTO myapp_systemstatus (
                    cpu_usage, ram_usage, disk_usage, mac_address,
                    ip_address, hostname, network_usage,
                    defender_status, firewall_status, auto_updates_status,
                    timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """
            cursor.execute(insert_query, (
                data["cpu_usage"], data["ram_usage"], data["disk_usage"],
                data["mac_address"], data["ip_address"], data["hostname"],
                data["network_usage"], data["defender_status"],
                data["firewall_status"], data["auto_updates_status"]
            ))

        # Commit the changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        print("Data sent to PostgreSQL successfully")
    except Exception as e:
        print(f"Error sending data to PostgreSQL: {e}")


while True:
    cpu_usage, ram_usage, disk_usage = get_system_info()
    mac_address, ip_address, hostname, network_usage = get_network_info()
    # ... (rest of your script remains unchanged)
    print_info("CPU Usage", f"{cpu_usage}%")
    print_info("RAM Usage", f"{ram_usage}%")
    print_info("Disk Usage", f"{disk_usage}%")
    print_info("MAC Address", mac_address)
    print_info("IP Address", ip_address)
    print_info("Hostname", hostname)
    print_info("Network Usage", f"{round(network_usage, 2)} MB")
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

    data = {
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage,
        "disk_usage": disk_usage,
        "mac_address": mac_address,
        "ip_address": ip_address,
        "hostname": hostname,
        "network_usage": round(network_usage, 2),
        "defender_status": windows_defender_status,
        "firewall_status": windows_firewall_status,
        "auto_updates_status": windows_auto_updates_status,
    }

    # Send data to PostgreSQL
    send_data_to_postgres(data)

    print("\n---\n")

    time.sleep(5)
