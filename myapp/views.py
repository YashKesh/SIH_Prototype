from django.http import HttpResponseServerError
import os
import platform
import socket
import wmi
import time
import pythoncom 
import datetime
import psutil
import time
from tabulate import tabulate
import win32api
import time
from django.shortcuts import render
from .utils import get_installed_apps
from .windows_lic import get_windows_information
import csv
import io
from datetime import datetime,time
from .models import LicenseData

# Create your views here.
def homepage(request):
    return render(request,'sidebar.html')

def mainhtml(request):
    return render(request,'main.html')

def get_random_mac_address():
    # Generate a random MAC address (Locally Administered Address)
    mac = [0x02, 0x42, 0xAC, 0x11, 0x00, 0x02]  # OUI (Organizationally Unique Identifier)
    for _ in range(6 - len(mac)):
        mac.append(os.urandom(1)[0] & 0xFE | 0x02)  # Randomize the last 6 bits while keeping the 2nd bit as '1'
    mac_address = ':'.join(map(lambda x: f'{x:02X}', mac))
    return mac_address
    
def get_system_info():
    try:
        pythoncom.CoInitialize()  # Initialize pythoncom

        # Hostname
        hostname = socket.gethostname()

        # Product Name
        product_name = platform.system() + " " + platform.release()

        # MAC Address
        mac_address = get_random_mac_address()

        # IP Address
        ip_address = socket.gethostbyname(hostname)

        # CPU Type and Speed
        c = wmi.WMI()
        cpu_info = c.Win32_Processor()[0]
        cpu_type = cpu_info.Name
        cpu_speed = f"{cpu_info.MaxClockSpeed} MHz"

        # Windows Build Number
        build_number = platform.win32_ver()[1]
        
        #date time
        current_Time = datetime.now().time()

        # Serial Number and Product ID (Windows-specific)
        try:
            c = wmi.WMI()
            os_info = c.Win32_OperatingSystem()[0]
            serial_number = os_info.SerialNumber
            product_id = os_info.SerialNumber
        except Exception:
            serial_number = "N/A"
            product_id = "N/A"

        # Print the collected information
        print("Hostname:", hostname)
        print("Product Name:", product_name)
        print("MAC Address:", mac_address)
        print("IP Address:", ip_address)
        print(f"CPU Type: {cpu_type}")
        print(f"CPU Speed: {cpu_speed}")
        print("Windows Build Number:", build_number)
        print("Serial Number:", serial_number)
        print("Product ID:", product_id)
        print("Current Time", current_Time)
    finally:
        pythoncom.CoUninitialize()  # Release pythoncom

    return {
        'hostname': hostname,
        'product_name': product_name,
        'mac_address': mac_address,
        'ip_address': ip_address,
        'cpu_type': cpu_type,
        'cpu_speed': cpu_speed,
        'build_number': build_number,
        'serial_number': serial_number,
        'product_id': product_id,
        'current_Time': current_Time
    }

if __name__ == "__main__":
    while True:
        print("Fetching System Information...")
        get_system_info()
        print("Waiting for 5 minutes...")
        time.sleep(300)  # Sleep for 5 minutes (300 seconds) before fetching information again

def get_publisher_and_version(file_path):
    try:
        file_info = win32api.GetFileVersionInfo(file_path, '\\')
        ms = file_info['FileVersionMS']
        ls = file_info['FileVersionLS']
        version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
        
        try:
            publisher = win32api.GetFileVersionInfo(file_path, "\\StringFileInfo\\040904b0\\CompanyName")
        except KeyError:
            publisher = "Unknown"
        
        return publisher, version
    except Exception as e:
        return "Unknown", "Unknown"

# def get_installed_apps():
#     apps = []
#     for root, dirs, files in os.walk(r'C:\Program Files'):
#         for file in files:
#             if file.endswith('.exe'):
#                 try:
#                     file_path = os.path.join(root, file)
#                     app_name = os.path.splitext(file)[0]
#                     publisher, version = get_publisher_and_version(file_path)
#                     installation_time = os.path.getctime(file_path)
#                     formatted_installation_time = datetime.datetime.fromtimestamp(installation_time).strftime('%Y-%m-%d %H:%M:%S')
#                     apps.append((app_name, publisher, formatted_installation_time, version))
#                 except Exception as e:
#                     pass
#     return apps



def get_system_usage():
    while True:
        # CPU Usage
        cpu_usage = psutil.cpu_percent(interval=1)
  
        # RAM Usage
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        unused_ram = 100 - ram_usage
        # Disk Usage (Combined)
        disk_info = psutil.disk_usage('/')
        disk_usage = f"Total: {disk_info.percent}% Used"
        diskempty = 100 - disk_info.percent

        # Print the collected information
        print(f"CPU Usage: {cpu_usage}")
        print(f"RAM Usage: {ram_usage}")
        print(f"Disk Usage: {disk_usage}")
        print(f"Unused ram: {unused_ram}")
        print(f"empty disk: {diskempty}")
        
        usage_data = {
        'cpu_usage': cpu_usage,
        'ram_usage': ram_usage,
        'disk_usage': disk_usage,
        'unused_ram':unused_ram,
        'diskempty':diskempty,
        'disk_info' : disk_info.percent}

        return usage_data

        # Sleep for 30 seconds
        time.sleep(30)

if __name__ == "__main__":
    print("Monitoring System Usage...")
    get_system_usage()    

def system_info(request):
    system_data = get_system_info()
    additional_data = get_system_usage()
    combined_data = {**system_data, **additional_data}
    return render(request, 'sys_info.html', {'data': combined_data})

def dashboard_system_info(request):
    system_data = get_system_info()
    additional_data = get_system_usage()
    combined_data = {**system_data, **additional_data}
    return render(request, 'dashboard.html', {'data': combined_data})

# def installed_apps_list(request):
#     installed_apps = get_installed_apps()
#     context = {'installed_apps': installed_apps}
#     return render(request, 'installed_apps.html', context)

def installed_apps(request):
    program_files_path = r'C:\Program Files'
    installed_apps = get_installed_apps(program_files_path)
    return render(request, 'installed_apps.html', {'installed_apps': installed_apps})



#windows license view
def windows_info(request):
    try:
        windows_info = get_windows_information()

        if windows_info:
            context = {
                "product_key": windows_info.product_key,
                "expiration_date": windows_info.expiration_date,
                "mac_address": windows_info.mac_address,
                "ip_address": windows_info.ip_address,
                "hostname": windows_info.hostname,
                "windows_version": windows_info.windows_version,
            }
            return render(request, "windows_lic.html", context)
        else:
            raise Exception("Failed to fetch Windows information.")
    except Exception as e:
        print(f"Error: {e}")
        return render(request, "error.html",e)
#windows license view










#custom configuration for the windows license view

  # Replace 'LicenseData' with the actual name of your model

def upload_csv(request):
    data = []

    try:
        if request.method == 'POST' and request.FILES['csv_file']:
            csv_file = request.FILES['csv_file']

            # Read CSV data
            decoded_file = csv_file.read().decode('utf-8-sig')
            reader = csv.reader(io.StringIO(decoded_file))

            # Get the header row
            header = next(reader, None)
            data.append(header)

            # Validate header and column count
            expected_header = ['Windows Product Key', 'License Expiration Date', 'MAC Address', 'IP Address', 'Hostname', 'Windows Version']
            if header != expected_header:
                raise ValueError("Invalid CSV header")

            # Define mapping between CSV column names and model field names
            field_mapping = {
                'Windows Product Key': 'windows_product_key',
                'License Expiration Date': 'license_expiration_date',
                'MAC Address': 'mac_address',
                'IP Address': 'ip_address',
                'Hostname': 'hostname',
                'Windows Version': 'windows_version',
            }

            for row in reader:
                # Validate column count
                if len(row) != len(expected_header):
                    raise ValueError("Invalid number of columns in CSV row")

                # Create a dictionary with the mapped field names
                row_data = {field_mapping[column]: value for column, value in zip(header, row)}
                try:
                    original_date = row_data['license_expiration_date']
                    original_date = original_date.replace('Sept', 'Sep')
                    # Replace the dot after the abbreviated month
                    original_date = original_date.replace('.', '')

                    # Convert to datetime object
                    date_object = datetime.strptime(original_date, "%b %d, %Y, %I:%M %p")

                    # Check if the time component is midnight
                    if date_object.time() == time(0, 0):
                        # If the time is midnight, set it to 00:00:00
                        formatted_date = date_object.strftime("%Y-%m-%d 00:00:00")
                    else:
                        # If the time is present, use the original time
                        formatted_date = date_object.strftime("%Y-%m-%d %H:%M:%S")
                    row_data['license_expiration_date'] = formatted_date
                except ValueError:
                    # Handle invalid date format gracefully
                    row_data['license_expiration_date'] = None

                # Check if the record already exists
                existing_record = LicenseData.objects.filter(
                    windows_product_key=row_data['windows_product_key'],
                    mac_address=row_data['mac_address']
                ).exists()

                if not existing_record:
                    # If the combination doesn't exist, insert the data into the database
                    LicenseData.objects.create(**row_data)
                    data.append(row)

    except ValueError as e:
        # Redirect to an error page if there's an issue with the CSV data
        return HttpResponseServerError(f"Error: {e}")
        # return render(request, "error.html")

    # Pass data to the template
    context = {'data': data}
    return render(request, 'custom_license.html', context)

# def upload_csv(request):
#     data = []

#     if request.method == 'POST' and request.FILES['csv_file']:
#         csv_file = request.FILES['csv_file']

#         # Read CSV data
#         decoded_file = csv_file.read().decode('utf-8-sig')
#         reader = csv.reader(io.StringIO(decoded_file))

#         for row in reader:
#             data.append(row)

#     # Pass data to the template
#     context = {'data': data}
#     return render(request, 'custom_license.html', context)

#end of the section 










#custom license database
def custom_license_update(request):
    return render(request,'custom_license_update.html')
