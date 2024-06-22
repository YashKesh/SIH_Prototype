import os
import platform
import psutil
import socket
import time
import psycopg2  # Import the psycopg2 library

def get_mac_address():
    try:
        with open('/sys/class/net/eth0/address') as file:
            return file.read().strip()
    except FileNotFoundError:
        return "Not available"

# ... (other functions remain unchanged)

def get_ip_address():
    try:
        # Iterate over network interfaces to find the first non-loopback IP address
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if not addr.address.startswith('127.') and ':' not in addr.address:
                    return addr.address
        return "Not available"
    except (psutil.Error, OSError):
        return "Not available"

def get_linux_distribution():
    try:
        with open('/etc/os-release') as file:
            for line in file:
                if line.startswith('PRETTY_NAME='):
                    return line.split('=')[1].strip().strip('"')
        return "Not available"
    except FileNotFoundError:
        return "Not available"

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_ram_usage():
    return psutil.virtual_memory().percent

def get_disk_usage():
    return psutil.disk_usage('/').percent

def get_network_usage():
    net_io = psutil.net_io_counters()
    sent_mb = net_io.bytes_sent / (1024 * 1024)  # Convert bytes to megabytes
    received_mb = net_io.bytes_recv / (1024 * 1024)  # Convert bytes to megabytes
    return sent_mb, received_mb

def get_host_name():
    return socket.gethostname()

def run_monitoring():
    # PostgreSQL connection details
    db_config = {
        'dbname': 'railway',
            'user': 'postgres',
            'password': 'CGa114-Be3geA1bge6-eDgA36425Gd5e',
            'host': 'viaduct.proxy.rlwy.net',
            'port': '27336'
    }

    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    while True:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        mac_id = get_mac_address()
        ip_address = get_ip_address()
        linux_distribution = get_linux_distribution()
        cpu_usage = get_cpu_usage()
        ram_usage = get_ram_usage()
        disk_usage = get_disk_usage()
        sent_mb, received_mb = get_network_usage()
        host_name = get_host_name()

        # Insert data into the PostgreSQL database with upsert (update or insert)
        insert_query = """
            INSERT INTO myapp_monitoringdata (
                timestamp, mac_id, ip_address, linux_distribution,
                cpu_usage, ram_usage, disk_usage, sent_mb, received_mb, host_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (mac_id) DO UPDATE
            SET
                timestamp = EXCLUDED.timestamp,
                ip_address = EXCLUDED.ip_address,
                linux_distribution = EXCLUDED.linux_distribution,
                cpu_usage = EXCLUDED.cpu_usage,
                ram_usage = EXCLUDED.ram_usage,
                disk_usage = EXCLUDED.disk_usage,
                sent_mb = EXCLUDED.sent_mb,
                received_mb = EXCLUDED.received_mb,
                host_name = EXCLUDED.host_name
        """
        data = (
            timestamp, mac_id, ip_address, linux_distribution,
            cpu_usage, ram_usage, disk_usage, sent_mb, received_mb, host_name
        )
        cursor.execute(insert_query, data)
        connection.commit()

        print(f"\n--- System Monitoring ---")
        print(f"Timestamp: {timestamp}")
        print(f"Mac ID: {mac_id}")
        print(f"IP Address: {ip_address}")
        print(f"Linux Distribution: {linux_distribution}")
        print(f"CPU Usage: {cpu_usage}%")
        print(f"RAM Usage: {ram_usage}%")
        print(f"Disk Usage: {disk_usage}%")
        print(f"Network Usage - Sent: {sent_mb:.2f} MB, Received: {received_mb:.2f} MB")
        print(f"Host Name: {host_name}")

        time.sleep(15)

    # Close the database connection when the script is interrupted or terminated
    cursor.close()
    connection.close()

if __name__ == "_main_":
    run_monitoring()