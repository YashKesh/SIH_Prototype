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
from django.shortcuts import get_object_or_404, render
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


from django.db.models import Avg
def dashboard_system_info(request):
    system_data = get_system_info()
    additional_data = get_system_usage()
    average_cpu_usage = SystemStatus.objects.aggregate(avg_cpu=Avg('cpu_usage'))['avg_cpu']
    num_devices_ram_greater_than_80 = SystemStatus.objects.filter(ram_usage__gt=80).count()
# RAM usage greater than 50 and less than or equal to 80
    num_devices_ram_between_50_and_80 = SystemStatus.objects.filter(ram_usage__gt=50, ram_usage__lte=80).count()
# RAM usage less than or equal to 50
    num_devices_ram_less_than_50 = SystemStatus.objects.filter(ram_usage__lte=50).count()
    total_system_status_entries = SystemStatus.objects.count()
    devices_greater_than_80 = MonitoringData.objects.filter(ram_usage__gt=80).count()

# Total number of devices with RAM less than 80 and greater than 50
    devices_between_50_and_80 = MonitoringData.objects.filter(ram_usage__lt=80, ram_usage__gt=50).count()

    # Total number of devices with RAM less than 50
    devices_less_than_50 = MonitoringData.objects.filter(ram_usage__lt=50).count()
    one_hour_ago = timezone.now() - timezone.timedelta(hours=1)

# Get the number of devices online (timestamp less than 1 hour ago)
    windows_devices_online = SystemStatus.objects.filter(timestamp__gte=one_hour_ago).count()
    linux_devices_online = MonitoringData.objects.filter(timestamp__gte=one_hour_ago).count()
    total_online = windows_devices_online + linux_devices_online
    average_ram_usage_windows = SystemStatus.objects.aggregate(avg_ram=Avg('ram_usage'))['avg_ram']
    average_ram_usage_linux = MonitoringData.objects.aggregate(avg_ram=Avg('ram_usage'))['avg_ram']
    if average_ram_usage_windows!=None and average_ram_usage_linux!=None:
        average = (average_ram_usage_windows + average_ram_usage_linux)//2
    else:
        average = 0
# Total number of entries in MonitoringData model
    total_monitoring_data_entries = MonitoringData.objects.count()
    total_devices = total_system_status_entries + total_monitoring_data_entries
    total_offline =   total_devices - total_online
    combined_data = {
        **system_data,
        **additional_data,
        'average_cpu_usage': average_cpu_usage,
        'num_devices_ram_greater_than_80': num_devices_ram_greater_than_80,
        'num_devices_ram_between_50_and_80': num_devices_ram_between_50_and_80,
        'num_devices_ram_less_than_50': num_devices_ram_less_than_50,
        'total_system_status_entries' : total_system_status_entries,
        'total_monitoring_data_entries' : total_monitoring_data_entries,
        'total_devices':total_devices,
        'devices_greater_than_80':devices_greater_than_80,
        'devices_between_50_and_80':devices_between_50_and_80,
        'devices_less_than_50':devices_less_than_50,
        'windows_devices_online':windows_devices_online,
        'linux_devices_online':linux_devices_online,
        'total_online':total_online,
        'total_offline':total_offline,
        'average':average,
    }
    return render(request, 'dashboard.html', {'data': combined_data})

# def installed_apps_list(request):
#     installed_apps = get_installed_apps()
#     context = {'installed_apps': installed_apps}
#     return render(request, 'installed_apps.html', context)
##
# views.py
from django.shortcuts import render
from .models import InstalledApp
from .utils import get_installed_apps  # Assuming you have a get_installed_apps function

def installed_apps(request):
    program_files_path = r'C:\Program Files'
    installed_apps_data = get_installed_apps(program_files_path)
    pythoncom.CoInitialize()
    wmi_obj = wmi.WMI()
    network_adapters = wmi_obj.Win32_NetworkAdapterConfiguration(IPEnabled=True)
    if network_adapters:
        mac_address = network_adapters[0].MACAddress
        ip_address = network_adapters[0].IPAddress[0]
    else:
        mac_address = "N/A"
        ip_address = "N/A"
    
    # Assuming you have access to the MAC address in the request (you might need to adjust this)
    for app_data in installed_apps_data:
        InstalledApp.objects.create(
            name=app_data['Name'],
            publisher=app_data['Publisher'],
            version=app_data['Version'],
            mac_address=mac_address,
        )

    return render(request, 'installed_apps.html', {'installed_apps': installed_apps_data})

##
# def installed_apps(request):
#     program_files_path = r'C:\Program Files'
#     installed_apps = get_installed_apps(program_files_path)
#     return render(request, 'installed_apps.html', {'installed_apps': installed_apps})



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
    
##manager access 
def windows_info1(request):
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
            return render(request, "windows_lic1.html", context)
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



##manager access
def upload_csv1(request):
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
    return render(request, 'custom_license1.html', context)

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




#api testing

#Api function testting 
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import WindowsInformationSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
# from .models import WindowsInformation
from .models import WindowsInformation
from .serializers import WindowsInformationSerializer
@api_view(['POST'])
def receive_windows_information(request):
    data = request.data
    serializer = WindowsInformationSerializer(data=data)

    if serializer.is_valid():
        # Try to get an existing entry by product key
        try:
            windows_info = WindowsInformation.objects.get(product_key=data['product_key'])
            serializer = WindowsInformationSerializer(windows_info, data=data)
        except WindowsInformation.DoesNotExist:
            pass  # No existing entry, create a new one

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(f"Serializer Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    print(f"Serializer Errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from .models import SystemUsage
from .serializers import SystemUsageSerializer
@api_view(['POST'])
def receive_system_usage(request):
    data = request.data
    product_key = data.get('product_key')

    # Try to get an existing entry by product key
    try:
        system_usage = SystemUsage.objects.get(product_key=product_key)
        serializer = SystemUsageSerializer(system_usage, data=data)
    except SystemUsage.DoesNotExist:
        # No existing entry, create a new one
        serializer = SystemUsageSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




#license data display

from django.shortcuts import render
from django.utils import timezone
from .models import WindowsInformation

def license_data_view(request):
    license_data = WindowsInformation.objects.all()

    for data in license_data:
        if data.expiration_date is not None:
            remaining_days = (data.expiration_date - timezone.now()).days
            data.status = f"{remaining_days} days remaining" if remaining_days > 0 else "Past Due"
        else:
            data.status = "N/A"

    return render(request, 'license_data.html', {'license_data': license_data})

##manager access
def license_data_view1(request):
    license_data = WindowsInformation.objects.all()

    for data in license_data:
        if data.expiration_date is not None:
            remaining_days = (data.expiration_date - timezone.now()).days
            data.status = f"{remaining_days} days remaining" if remaining_days > 0 else "Past Due"
        else:
            data.status = "N/A"

    return render(request, 'license_data1.html', {'license_data': license_data})

### for exporting the data into scv format
from django.http import HttpResponse
import csv
from django.utils import timezone
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=license_data.csv'

    writer = csv.writer(response)
    writer.writerow(['Windows Product Key', 'License Expiration Date', 'Remaining Days', 'MAC Address', 'IP Address', 'Hostname', 'Windows Version'])

    license_data = LicenseData.objects.all()

    for data in license_data:
        remaining_days = (data.license_expiration_date - timezone.now()).days if data.license_expiration_date else None
        status = f"{remaining_days} days remaining" if remaining_days and remaining_days > 0 else "Past Due"

        writer.writerow([
            data.windows_product_key,
            str(data.license_expiration_date) if data.license_expiration_date else '',
            status,
            data.mac_address,
            str(data.ip_address),
            data.hostname,
            data.windows_version,
        ])

    return response


##


from .serializers import SystemStatusSerializer
from .models import SystemStatus
## security Status view api 
@api_view(['POST'])
def receive_system_status(request):
    try:
        # Check if the MAC address exists in the database
        mac_address = request.data.get('mac_address')
        system_status = SystemStatus.objects.get(mac_address=mac_address)
        serializer = SystemStatusSerializer(system_status, data=request.data)
    except SystemStatus.DoesNotExist:
        # If the MAC address does not exist, create a new record
        serializer = SystemStatusSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# api data display on the UI
##logic for the objective function
def compute_overall_performance(cpu_usage, memory_usage, disk_usage):
    # Weights for each metric (you can adjust these based on your priorities)
    cpu_weight = 0.4
    memory_weight = 0.3
    disk_weight = 0.3  # Adjusted the weights to sum up to 1.0 without temperature

    # Normalize the metrics to be in the range [0, 1]
    normalized_cpu = min(cpu_usage / 100, 1.0)
    normalized_memory = min(memory_usage / 100, 1.0)
    normalized_disk = min(disk_usage / 100, 1.0)

    # Calculate the overall performance score out of 10
    overall_performance = (
        cpu_weight * (1 - normalized_cpu) +
        memory_weight * (1 - normalized_memory) +
        disk_weight * (1 - normalized_disk)
    ) * 10

    return overall_performance

def categorize_performance(overall_performance):
    # Define inverted thresholds for performance categories
    critical_threshold = 5.0
    high_threshold = 3.0
    medium_threshold = 3.0

    # Categorize based on inverted thresholds
    if overall_performance <= critical_threshold:
        return "Critical"
    elif overall_performance <= high_threshold:
        return "High"
    else:
        return "Clear"


from .models import SystemStatus    
def system_status_view(request):
    system_status_data = SystemStatus.objects.all()  # You might want to add ordering or filtering here
    for status in system_status_data:
        timing = round(( timezone.now() - status.timestamp).total_seconds() / 3600,2)
        status.last_updated = f"{timing} hours" if timing>1 else "now"
        status.status = "Online" if timing<1 else "Offline"
        status.network_usage = f"{round(status.network_usage, 2)} MB"
        status.defender_value = "Enabled" if status.defender_status else "Disabled"
        status.firewall_value = "Enabled" if status.firewall_status else "Disabled"
        status.auto_update  = "Enabled" if status.auto_updates_status else "Disabled"
        status.performance = compute_overall_performance(status.cpu_usage,status.ram_usage,status.disk_usage)
        status.condition = categorize_performance(status.performance)
    return render(request, 'system_status_list.html', {'system_status_data': system_status_data})


##manager access
from .models import SystemStatus    
def system_status_view1(request):
    system_status_data = SystemStatus.objects.all()  # You might want to add ordering or filtering here
    for status in system_status_data:
        timing = round(( timezone.now() - status.timestamp).total_seconds() / 3600,2)
        status.last_updated = f"{timing} hours" if timing>1 else "now"
        status.status = "Online" if timing<1 else "Offline"
        status.network_usage = f"{round(status.network_usage, 2)} MB"
        status.defender_value = "Enabled" if status.defender_status else "Disabled"
        status.firewall_value = "Enabled" if status.firewall_status else "Disabled"
        status.auto_update  = "Enabled" if status.auto_updates_status else "Disabled"
        if status.cpu_usage*100 > 80 and status.ram_usage>80:
            status.condition  = "Critical"
        elif status.cpu_usage*100>50 and status.ram_usage>50:
            status.condition = "High"
        else:
            status.condition = "Clear"
    return render(request, 'system_status_list1.html', {'system_status_data': system_status_data})



### Custom firewall view 
from django.http import HttpResponse
from django.shortcuts import render
from .models import Firewall
import xlwt

def firewall_list(request):
    firewalls = Firewall.objects.all()

    if 'export_excel' in request.GET:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="firewalls.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Firewalls')

        # Write headers
        row_num = 0
        columns = ['Name', 'IP', 'Port', 'Location', 'Description', 'Link']
        for col_num, column_title in enumerate(columns):
            ws.write(row_num, col_num, column_title)

        # Write data
        for firewall in firewalls:
            row_num += 1
            ws.write(row_num, 0, firewall.name)
            ws.write(row_num, 1, firewall.ip)
            ws.write(row_num, 2, firewall.port)
            ws.write(row_num, 3, firewall.location)
            ws.write(row_num, 4, firewall.description)
            ws.write(row_num, 5, firewall.link)

        wb.save(response)
        return response

    return render(request, 'firewall_list.html', {'firewalls': firewalls})

## firewall manager views
def firewall_list1(request):
    firewalls = Firewall.objects.all()

    if 'export_excel' in request.GET:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="firewalls.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Firewalls')

        # Write headers
        row_num = 0
        columns = ['Name', 'IP', 'Port', 'Location', 'Description', 'Link']
        for col_num, column_title in enumerate(columns):
            ws.write(row_num, col_num, column_title)

        # Write data
        for firewall in firewalls:
            row_num += 1
            ws.write(row_num, 0, firewall.name)
            ws.write(row_num, 1, firewall.ip)
            ws.write(row_num, 2, firewall.port)
            ws.write(row_num, 3, firewall.location)
            ws.write(row_num, 4, firewall.description)
            ws.write(row_num, 5, firewall.link)

        wb.save(response)
        return response

    return render(request, 'firewall_list1.html', {'firewalls': firewalls})
## manager ends for firewall

# views.py
from django.shortcuts import render, redirect
from .forms import FirewallForm
from .models import Firewall

def firewall_create(request):
    if request.method == 'POST':
        form = FirewallForm(request.POST)
        if form.is_valid():
            # Get the form data
            firewall_instance = form.save(commit=False)

            # Generate the link using the provided logic
            firewall_instance.link = f"https://{firewall_instance.ip}:{firewall_instance.port}"

            # Save the updated instance to the database
            firewall_instance.save()

            return redirect('firewall_list')

    else:
        form = FirewallForm()

    return render(request, 'firewall_create.html', {'form': form})

## manager creation 
def firewall_create1(request):
    if request.method == 'POST':
        form = FirewallForm(request.POST)
        if form.is_valid():
            # Get the form data
            firewall_instance = form.save(commit=False)

            # Generate the link using the provided logic
            firewall_instance.link = f"https://{firewall_instance.ip}:{firewall_instance.port}"

            # Save the updated instance to the database
            firewall_instance.save()

            return redirect('firewall_list')

    else:
        form = FirewallForm()

    return render(request, 'firewall_create1.html', {'form': form})


def firewall_edit(request, pk):
    firewall = get_object_or_404(Firewall, pk=pk)

    if request.method == 'POST':
        form = FirewallForm(request.POST, instance=firewall)
        if form.is_valid():
            form.save()
            return redirect('firewall_list')
    else:
        form = FirewallForm(instance=firewall)

    return render(request, 'firewall_edit.html', {'form': form, 'firewall': firewall})
##manager edit
def firewall_edit1(request, pk):
    firewall = get_object_or_404(Firewall, pk=pk)

    if request.method == 'POST':
        form = FirewallForm(request.POST, instance=firewall)
        if form.is_valid():
            form.save()
            return redirect('firewall_list')
    else:
        form = FirewallForm(instance=firewall)

    return render(request, 'firewall_edit.html', {'form': form, 'firewall': firewall})

def firewall_delete(request, pk):
    firewall = get_object_or_404(Firewall, pk=pk)
    
    if request.method == 'POST':
        firewall.delete()
        return redirect('firewall_list')

    return render(request, 'firewall_delete.html', {'firewall': firewall})

##manager delete 
def firewall_delete1(request, pk):
    firewall = get_object_or_404(Firewall, pk=pk)
    
    if request.method == 'POST':
        firewall.delete()
        return redirect('firewall_list')

    return render(request, 'firewall_delete1.html', {'firewall': firewall})

####


## clickable eventn 
# views.py
# from django.shortcuts import render, get_object_or_404
# from .models import SystemStatus

# def device_detail(request, mac_address):
#     system_status = get_object_or_404(SystemStatus, mac_address=mac_address)
#     return render(request, 'device_detail.html', {'system_status': system_status})

from django.shortcuts import render, get_object_or_404
from .models import SystemStatus, InstalledApp
from django.core.mail import send_mail
def device_detail(request, mac_address):
    system_status = get_object_or_404(SystemStatus, mac_address=mac_address)
    temperature_reading = get_object_or_404(TemperatureReading, mac_address=mac_address)

    # Extract numeric value from the temperature field using regex
    numeric_temperature = re.search(r'\d+', temperature_reading.temperature)
    if numeric_temperature:
        trimmed_temperature = numeric_temperature.group()
    else:
        trimmed_temperature = None
    if trimmed_temperature !=None:
        trimmed_temperature = int(trimmed_temperature)
        trimmed_temperature = round(((trimmed_temperature/10)-273.5),2)
    # Update system_status with trimmed temperature
    system_status.temperature = trimmed_temperature
    system_status.defender_value = "Enabled" if system_status.defender_status else "Disabled"
    system_status.firewall_value = "Enabled" if system_status.firewall_status else "Disabled"
    system_status.auto_update  = "Enabled" if system_status.auto_updates_status else "Disabled"
    system_status.performance = compute_overall_performance(system_status.cpu_usage,system_status.ram_usage,system_status.disk_usage)
    system_status.condition = categorize_performance(system_status.performance)
    # Query installed apps based on the mac_address
    installed_apps = InstalledApp.objects.filter(mac_address=mac_address)
    
    return render(request, 'device_detail.html', {'system_status': system_status, 'installed_apps': installed_apps})
from django.conf import settings
##send theh mail 
def send_alert_email(mac_address, condition):
    subject = f"Critical Alert for Device: {mac_address}"
    message = f"The device with MAC address {mac_address} is in a critical condition: {condition}."

    # Replace the following with your actual email addresses
    from_email =  settings.EMAIL_HOST_USER 
    to_email = ["prathampoojari1@gmail.com"]

    # Use the send_mail function to send the email
    send_mail(subject, message, from_email, to_email)
##manager access
def device_detail1(request, mac_address):
    system_status = get_object_or_404(SystemStatus, mac_address=mac_address)
    
    system_status.defender_value = "Enabled" if system_status.defender_status else "Disabled"
    system_status.firewall_value = "Enabled" if system_status.firewall_status else "Disabled"
    system_status.auto_update  = "Enabled" if system_status.auto_updates_status else "Disabled"
    if system_status.cpu_usage*100 > 80 and system_status.ram_usage>80:
        system_status.condition  = "Critical"
    elif system_status.cpu_usage*100>50 and system_status.ram_usage>50:
        system_status.condition = "High"
    else:
        system_status.condition = "Clear"
    # Query installed apps based on the mac_address
    installed_apps = InstalledApp.objects.filter(mac_address=mac_address)
    
    return render(request, 'device_detail1.html', {'system_status': system_status, 'installed_apps': installed_apps})

## linux distribution view 
from django.shortcuts import render
from .models import MonitoringData  # Adjust the import based on your app structure

def monitoring_data_view(request):
    monitoring_data_objects = MonitoringData.objects.all()
    for status in monitoring_data_objects:
        timing = round(( timezone.now() - status.timestamp).total_seconds() / 3600,2)
        status.last_updated = f"{timing} hours" if timing>1 else "now"
        status.status = "Online" if timing<1 else "Offline"
        if status.cpu_usage*100 > 80 and status.ram_usage>80:
            status.condition  = "Critical"
        elif status.cpu_usage*100>50 and status.ram_usage>50:
            status.condition = "High"
        else:
            status.condition = "Clear"
    context = {'monitoring_data_objects': monitoring_data_objects}
    return render(request, 'monitoring_data_linux.html', context)


def linux_detail(request, mac_address):
    monitoring_data = MonitoringData.objects.get(mac_id=mac_address)
    context = {'monitoring_data': monitoring_data}
    return render(request, 'linux_detail.html', context)

### windows access

def monitoring_data_view1(request):
    monitoring_data_objects = MonitoringData.objects.all()
    for status in monitoring_data_objects:
        timing = round(( timezone.now() - status.timestamp).total_seconds() / 3600,2)
        status.last_updated = f"{timing} hours" if timing>1 else "now"
        status.status = "Online" if timing<1 else "Offline"
        if status.cpu_usage*100 > 80 and status.ram_usage>80:
            status.condition  = "Critical"
        elif status.cpu_usage*100>50 and status.ram_usage>50:
            status.condition = "High"
        else:
            status.condition = "Clear"
    context = {'monitoring_data_objects': monitoring_data_objects}
    return render(request, 'monitoring_data_linux1.html', context)


def linux_detail1(request, mac_address):
    monitoring_data = MonitoringData.objects.get(mac_id=mac_address)
    context = {'monitoring_data': monitoring_data}
    return render(request, 'linux_detail1.html', context)
### Router code 
# views.py
from django.views.generic import ListView
from .models import Router

def routerview(request):
    router_data = Router.objects.all()
    context = {'router_data':router_data}
    return render(request,'router.html',context)



def router_detail(request, Name):
    system_status = get_object_or_404(Router, Name=Name)
    system_status.link = f"http://{system_status.IP_address}:{system_status.port}"
    return render(request, 'router_detail.html', {'system_status': system_status})

###login trial 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login

@login_required
def dashboard(request):
    if request.user.is_superuser:
        return redirect('dashboard_main')
    else:
        print(f"User is not a superuser. User: {request.user.username}")
        return render(request, 'dashboard1.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Check the username and redirect accordingly
            if user.username == 'firewall_manager':
                return redirect('firewall_list1')
            elif user.username == 'windows_manager':        # Redirect to firewall dashboard
                return redirect('system_status_view1')
            else:
                return redirect('dashboard')  # Redirect to the default dashboard
            
        else:
            messages.error(request, 'Invalid login credentials. Please try again.') 

    return render(request, 'login.html')



### logout
from django.contrib.auth import logout
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page


##log upload and display
# views.py
import csv
import re
from django.shortcuts import render, redirect
from .forms import LogUploadForm
from .models import LogEntry
from io import TextIOWrapper

def upload_and_display_log(request):
    log_entries = LogEntry.objects.all()

    if request.method == 'POST':
        form = LogUploadForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_log(request.FILES['log_file'])
            return redirect('upload_and_display_log')
    else:
        form = LogUploadForm()

    return render(request, 'log_upload_and_display.html', {'form': form, 'log_entries': log_entries})

def handle_uploaded_log(file):
    decoded_file = TextIOWrapper(file, encoding='utf-8')
    csv_reader = csv.reader(decoded_file)

    for row in csv_reader:
        if len(row) == 2:
            log_data = parse_log_entry(row[0], row[1])

            if log_data:
                log_entry = LogEntry.objects.create(**log_data)
                log_entry.save()

def parse_log_entry(first_column, second_column):
    try:
        # Regular expression to extract information from the first column
        first_column_pattern = re.compile(r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)\s+(?P<ip_address>[0-9.:]+)\s+(?P<response_time>\d+\.\d+)\s+(?P<http_status_code>\d+)')
        first_column_match = first_column_pattern.search(first_column)

        if not first_column_match:
            return None

        # Extracted information from the first column
        timestamp = first_column_match.group('timestamp')
        source_ip = first_column_match.group('ip_address')
        response_time = float(first_column_match.group('response_time'))
        http_status_code = int(first_column_match.group('http_status_code'))

        # Extracted information from the second column
        second_column_pattern = re.compile(r'"(?P<http_method>\w+) (?P<url>[^"]+)" "(?P<user_agent>[^"]+)"')
        second_column_match = second_column_pattern.search(second_column)

        if not second_column_match:
            return None

        http_method = second_column_match.group('http_method')
        url = second_column_match.group('url')
        user_agent = second_column_match.group('user_agent')

        # Create a dictionary to store the parsed data
        log_data = {
            'timestamp': timestamp,
            'source_ip': source_ip,
            'response_time': response_time,
            'http_status_code': http_status_code,
            'http_method': http_method,
            'url': url,
            'user_agent': user_agent,
            # Add more fields as needed
        }

        return log_data

    except Exception as e:
        print(f"Error parsing log entry: {e}")
        return None

###temperarture of the system 
# views.py in your Django app

from django.shortcuts import render
from .models import TemperatureReading

def temperature_reading_view(request):
    # Fetch all temperature readings from the database
    readings = TemperatureReading.objects.all()
    # Pass the readings to the template
    context = {'readings': readings}

    # Render the template with the readings data
    return render(request, 'temperature_reading_template.html', context)

