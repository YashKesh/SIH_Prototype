import wmi
from datetime import datetime, timedelta
import traceback  # Added for better error handling

class WindowsInformation:
    def __init__(self, product_key, expiration_date, mac_address, ip_address, hostname, windows_version):
        self.product_key = product_key
        self.expiration_date = expiration_date
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.hostname = hostname
        self.windows_version = windows_version

import pythoncom  # Import the pythoncom module

def get_windows_information():
    try:
        # Initialize COM
        pythoncom.CoInitialize()  # Add this line

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



windows_info = get_windows_information()

if windows_info:
    print(f"Windows Product Key: {windows_info.product_key}")
    print(f"License Expiration Date: {windows_info.expiration_date}")
    print(f"MAC Address: {windows_info.mac_address}")
    print(f"IP Address: {windows_info.ip_address}")
    print(f"Hostname: {windows_info.hostname}")
    print(f"Windows Version: {windows_info.windows_version}")
else:
    print("Failed to fetch Windows information.")