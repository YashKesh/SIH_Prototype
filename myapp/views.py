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
        'total_offline':total_offline
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
        if status.cpu_usage*100 > 80 and status.ram_usage>80:
            status.condition  = "Critical"
        elif status.cpu_usage*100>50 and status.ram_usage>50:
            status.condition = "High"
        else:
            status.condition = "Clear"
    return render(request, 'system_status_list.html', {'system_status_data': system_status_data})



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

def firewall_delete(request, pk):
    firewall = get_object_or_404(Firewall, pk=pk)
    
    if request.method == 'POST':
        firewall.delete()
        return redirect('firewall_list')

    return render(request, 'firewall_delete.html', {'firewall': firewall})

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

def device_detail(request, mac_address):
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
    
    return render(request, 'device_detail.html', {'system_status': system_status, 'installed_apps': installed_apps})



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


