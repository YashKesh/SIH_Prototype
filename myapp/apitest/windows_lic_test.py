import requests
import wmi
from datetime import datetime, timedelta
import traceback
import pythoncom
import time

class WindowsInformation:
    def __init__(self, product_key, expiration_date, mac_address, ip_address, hostname, windows_version):
        self.product_key = product_key
        self.expiration_date = expiration_date
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.hostname = hostname
        self.windows_version = windows_version

def send_windows_information_to_api(windows_info):
    try:
        url = 'http://127.0.0.1:8000/api/receive_windows_information/'  # Replace with your API endpoint

        # Convert WindowsInformation object to a dictionary for serialization
        windows_info_dict = {
            'product_key': windows_info.product_key,
            'expiration_date': str(windows_info.expiration_date),
            'mac_address': windows_info.mac_address,
            'ip_address': windows_info.ip_address,
            'hostname': windows_info.hostname,
            'windows_version': windows_info.windows_version,
        }

        # Send the data to your API with the content type set to JSON
        response = requests.post(url, json=windows_info_dict, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        print("Data sent to API successfully")

    except Exception as e:
        print(f"Error in send_windows_information_to_api: {e}")
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

while True:
    windows_info = get_windows_information()

    if windows_info:
        print(f"Windows Product Key: {windows_info.product_key}")
        print(f"License Expiration Date: {windows_info.expiration_date}")
        print(f"MAC Address: {windows_info.mac_address}")
        print(f"IP Address: {windows_info.ip_address}")
        print(f"Hostname: {windows_info.hostname}")
        print(f"Windows Version: {windows_info.windows_version}")

        # Send data to Django server
        send_windows_information_to_api(windows_info)
    else:
        print("Failed to fetch Windows information.")
    # Sleep for a certain interval (e.g., 30 seconds) before the next iteration
    time.sleep(30)
