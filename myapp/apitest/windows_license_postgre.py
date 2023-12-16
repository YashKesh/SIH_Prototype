import requests
import wmi
from datetime import datetime, timedelta
import traceback
import pythoncom
import time
import psycopg2

class WindowsInformation:
    def __init__(self, product_key, expiration_date, mac_address, ip_address, hostname, windows_version):
        self.product_key = product_key
        self.expiration_date = expiration_date
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.hostname = hostname
        self.windows_version = windows_version

def send_windows_information_to_postgres(windows_info):
    try:
        # PostgreSQL connection parameters
        postgres_params = {
            'dbname': 'railway',
            'user': 'postgres',
            'password': 'CFEfe2aB5*GecE5gFgbDD53Bd*-124Gc',
            'host': 'monorail.proxy.rlwy.net',
            'port': '54739'
        }

        # Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(**postgres_params)
        cursor = connection.cursor()

        # Check if the record with the given product_key already exists
        select_query = "SELECT product_key FROM myapp_windowsinformation WHERE product_key = %s"
        cursor.execute(select_query, (windows_info.product_key,))
        existing_record = cursor.fetchone()

        if not existing_record:
            # Insert a new record
            insert_query = """
                INSERT INTO myapp_windowsinformation (
                    product_key, expiration_date, mac_address,
                    ip_address, hostname, windows_version
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                windows_info.product_key, windows_info.expiration_date,
                windows_info.mac_address, windows_info.ip_address,
                windows_info.hostname, windows_info.windows_version
            ))

            # Commit the changes and close the connection
            connection.commit()
            cursor.close()
            connection.close()

            print("Windows information sent to PostgreSQL successfully")
        else:
            print("Windows information already exists in PostgreSQL. Skipping insertion.")

    except Exception as e:
        print(f"Error sending data to PostgreSQL: {e}")
        traceback.print_exc()

def get_windows_information():
    try:
        # Initialize COM
        pythoncom.CoInitialize()

        wmi_obj = wmi.WMI()

        os_info = wmi_obj.Win32_OperatingSystem()[0]
        product_key = os_info.SerialNumber if os_info.SerialNumber else os_info.ProductKey

        install_date = os_info.InstallDate.split('.')[0]
        install_date = datetime.strptime(install_date, "%Y%m%d%H%M%S")
        expiration_date = install_date + timedelta(days=365)

        network_adapters = wmi_obj.Win32_NetworkAdapterConfiguration(IPEnabled=True)
        if network_adapters:
            mac_address = network_adapters[0].MACAddress
            ip_address = network_adapters[0].IPAddress[0]
        else:
            mac_address = "N/A"
            ip_address = "N/A"

        computer_system = wmi_obj.Win32_ComputerSystem()[0]
        hostname = computer_system.Caption

        windows_version = os_info.Caption

        return WindowsInformation(product_key, expiration_date, mac_address, ip_address, hostname, windows_version)
    except Exception as e:
        print(f"Error in get_windows_information: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    windows_info = get_windows_information()

    if windows_info:
        print(f"Windows Product Key: {windows_info.product_key}")
        print(f"License Expiration Date: {windows_info.expiration_date}")
        print(f"MAC Address: {windows_info.mac_address}")
        print(f"IP Address: {windows_info.ip_address}")
        print(f"Hostname: {windows_info.hostname}")
        print(f"Windows Version: {windows_info.windows_version}")

        # Send data to PostgreSQL
        send_windows_information_to_postgres(windows_info)
    else:
        print("Failed to fetch Windows information.")
