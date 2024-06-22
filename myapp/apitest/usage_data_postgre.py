import requests
import psutil
import wmi
import time
import psycopg2

class SystemUsage:
    def __init__(self, product_key, cpu_usage, ram_usage, disk_usage, unused_ram, diskempty, disk_info):
        self.product_key = product_key
        self.cpu_usage = cpu_usage
        self.ram_usage = ram_usage
        self.disk_usage = disk_usage
        self.unused_ram = unused_ram
        self.diskempty = diskempty
        self.disk_info = disk_info

def send_system_usage_to_postgres(system_usage):
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

        # Check if the record with the given product_key already exists
        select_query = "SELECT product_key FROM myapp_systemusage WHERE product_key = %s"
        cursor.execute(select_query, (system_usage.product_key,))
        existing_record = cursor.fetchone()

        if existing_record:
            # Update the existing record
            update_query = """
                UPDATE myapp_systemusage
                SET cpu_usage = %s, ram_usage = %s, disk_usage = %s,
                    unused_ram = %s, diskempty = %s, disk_info = %s
                WHERE product_key = %s
            """
            cursor.execute(update_query, (
                system_usage.cpu_usage, system_usage.ram_usage, system_usage.disk_usage,
                system_usage.unused_ram, system_usage.diskempty, system_usage.disk_info,
                system_usage.product_key
            ))
        else:
            # Insert a new record
            insert_query = """
                INSERT INTO myapp_systemusage (
                    product_key, cpu_usage, ram_usage, disk_usage,
                    unused_ram, diskempty, disk_info
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                system_usage.product_key, system_usage.cpu_usage, system_usage.ram_usage,
                system_usage.disk_usage, system_usage.unused_ram, system_usage.diskempty,
                system_usage.disk_info
            ))

        # Commit the changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        print("System usage information sent to PostgreSQL successfully")
    except Exception as e:
        print(f"Error sending data to PostgreSQL: {e}")

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
        send_system_usage_to_postgres(system_usage_data)
