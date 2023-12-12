import requests
import psutil
import wmi
import time

class SystemUsage:
    def __init__(self, product_key, cpu_usage, ram_usage, disk_usage, unused_ram, diskempty, disk_info):
        self.product_key = product_key
        self.cpu_usage = cpu_usage
        self.ram_usage = ram_usage
        self.disk_usage = disk_usage
        self.unused_ram = unused_ram
        self.diskempty = diskempty
        self.disk_info = disk_info

def send_system_usage_to_django(system_usage):
    try:
        url = 'http://127.0.0.1:8000//api/receive_system_usage/'

        # Convert SystemUsage object to a dictionary for serialization
        system_usage_dict = {
            'product_key': system_usage.product_key,
            'cpu_usage': system_usage.cpu_usage,
            'ram_usage': system_usage.ram_usage,
            'disk_usage': system_usage.disk_usage,
            'unused_ram': system_usage.unused_ram,
            'diskempty': system_usage.diskempty,
            'disk_info': system_usage.disk_info,
        }

        # Send the data to Django server as JSON
        response = requests.post(url, json=system_usage_dict, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        print("System usage information sent to Django server successfully")

    except Exception as e:
        print(f"Error in send_system_usage_to_django: {e}")

def get_system_usage():
    while True:
        wmi_obj = wmi.WMI()
        os_info = wmi_obj.Win32_OperatingSystem()[0]
        product_key = os_info.SerialNumber if os_info.SerialNumber else os_info.ProductKey

        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        unused_ram = 100 - ram_usage
        disk_info = psutil.disk_usage('/')
        disk_usage = f"Total: {disk_info.percent}% Used"
        diskempty = 100 - disk_info.percent

        usage_data = {
            'product_key': product_key,
            'cpu_usage': cpu_usage,
            'ram_usage': ram_usage,
            'disk_usage': disk_usage,
            'unused_ram': unused_ram,
            'diskempty': diskempty,
            'disk_info': disk_info.percent,
        }

        yield SystemUsage(**usage_data)
        time.sleep(30)  # Sleep for 30 seconds before collecting the next set of data

if __name__ == "__main__":
    system_usage_generator = get_system_usage()
    for system_usage_data in system_usage_generator:
        send_system_usage_to_django(system_usage_data)
