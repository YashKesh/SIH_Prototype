import os
import datetime
from tabulate import tabulate
import win32api
import time


def get_publisher_and_version(file_path):
    try:
        file_info = win32api.GetFileVersionInfo(file_path, '\\')
        ms, ls = file_info['FileVersionMS'], file_info['FileVersionLS']
        version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"

        try:
            publisher = win32api.GetFileVersionInfo(
                file_path, "\\StringFileInfo\\040904b0\\CompanyName")
        except KeyError:
            publisher = "Unknown"

        return publisher, version
    except Exception as e:
        return "Unknown", "Unknown"


def fetch_name_from_internet(publisher, version):
    # Replace this with your actual logic to fetch the name from the internet
    # For example, you might use an API call to retrieve information based on publisher and version
    # Here, we are returning an empty string as a placeholder
    return ""


def get_installed_apps(program_files_path):
    installed_apps = {}

    for root, dirs, files in os.walk(program_files_path):
        for file in files:
            if file.endswith('.exe'):
                try:
                    file_path = os.path.join(root, file)
                    app_name = os.path.splitext(file)[0]

                    # Exclude apps with the word "uninstall" in the name
                    if "uninstall" not in app_name.lower():
                        publisher, version = get_publisher_and_version(
                            file_path)
                        installation_time = os.path.getctime(file_path)
                        formatted_installation_time = datetime.datetime.fromtimestamp(
                            installation_time).strftime('%Y-%m-%d %H:%M:%S')

                        key = (publisher, version)
                        if key not in installed_apps:
                            # Application with the same version and publisher doesn't exist
                            # Fetch the name from the internet based on version and publisher
                            name_from_internet = fetch_name_from_internet(
                                publisher, version)
                            installed_apps[key] = {
                                'Name': name_from_internet if name_from_internet else app_name,
                                'Publisher': publisher,
                                'Version': version,
                                'Installed On': formatted_installation_time,
                            }
                except Exception as e:
                    pass

    return list(installed_apps.values())