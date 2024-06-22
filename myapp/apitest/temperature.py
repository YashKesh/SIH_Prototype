import wmi
import psycopg2
from datetime import datetime

# PostgreSQL database connection parameters
db_params = {
    'dbname': 'railway',
        'user': 'postgres',
        'password': 'CGa114-Be3geA1bge6-eDgA36425Gd5e',
        'host': 'viaduct.proxy.rlwy.net',
        'port': '27336'
}

def get_network_info():
    try:
        wmi_obj = wmi.WMI()

        # Get MAC Address, IP Address, and Hostname of the primary network adapter (if available)
        network_adapter = wmi_obj.Win32_NetworkAdapterConfiguration(
            IPEnabled=True)
        if network_adapter:
            mac_address = network_adapter[0].MACAddress
        else:
            mac_address = "N/A"

        return mac_address
    except Exception as e:
        print(f"Error fetching network information: {e}")
        return None

def remove_null_characters(input_str):
    return input_str.replace('\x00', '')

def collect_and_store_data(file_path):
    cursor = None
    connection = None

    try:
        # Open the text file in read mode
        with open(file_path, 'r') as file:
            # Read the content of the file into a string variable
            file_content = file.read()

            # Remove NUL characters from the string
            file_content = remove_null_characters(file_content)

            # Get network information
            mac_address = get_network_info()

            # Extract temperature data (modify this based on your file content)
            # Assuming file contains a float
            temperature_data = str(file_content.strip())

            # Connect to the PostgreSQL database
            connection = psycopg2.connect(**db_params)

            # Create a cursor
            cursor = connection.cursor()

            # Check if a record with the given MAC address already exists
            cursor.execute("SELECT * FROM myapp_temperaturereading WHERE mac_address = %s", (mac_address,))
            existing_record = cursor.fetchone()

            if existing_record:
                # If record exists, update the temperature
                update_sql = "UPDATE myapp_temperaturereading SET temperature = %s, timestamp = %s WHERE mac_address = %s"
                timestamp = datetime.now()
                cursor.execute(update_sql, (temperature_data, timestamp, mac_address))
            else:
                # If record doesn't exist, create a new entry
                insert_sql = "INSERT INTO myapp_temperaturereading (mac_address, temperature, timestamp) VALUES (%s, %s, %s)"
                timestamp = datetime.now()
                cursor.execute(insert_sql, (mac_address, temperature_data, timestamp))

            # Commit the transaction
            connection.commit()

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error collecting and storing data: {e}")
    finally:
        # Close the cursor and connection in the 'finally' block to ensure cleanup
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Specify the path to the text file
file_path = 'C:\\Windows\\System32\\OUTPUT.txt'
collect_and_store_data(file_path)