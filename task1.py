import sys
import os
import time
import platform
import subprocess
import json
from concurrent.futures import ProcessPoolExecutor

if __name__ == "__main__":
    processor = platform.processor() or platform.machine()
    physical_cores = "Unavailable"
    logical_cores = os.cpu_count()
    current_frequency = "Unavailable"
    maximum_frequency = "Unavailable"
    student_id = 230103192

    # Query the actual Windows hardware without additional Python packages.
    if platform.system() == "Windows":
        try:
            command = (
                "Get-CimInstance Win32_Processor | "
                "Select-Object Name, NumberOfCores, "
                "NumberOfLogicalProcessors, CurrentClockSpeed, MaxClockSpeed | "
                "ConvertTo-Json -Compress"
            )

            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", command],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )

            cpu_data = json.loads(result.stdout.strip())

            if isinstance(cpu_data, dict):
                cpu_data = [cpu_data]

            processor = "; ".join(cpu["Name"].strip() for cpu in cpu_data)
            physical_cores = sum(cpu["NumberOfCores"] for cpu in cpu_data)
            logical_cores = sum(
                cpu["NumberOfLogicalProcessors"] for cpu in cpu_data
            )
            current_frequency = "; ".join(
                f'{cpu["CurrentClockSpeed"]} MHz' for cpu in cpu_data
            )
            maximum_frequency = "; ".join(
                f'{cpu["MaxClockSpeed"]} MHz' for cpu in cpu_data
            )

        except (
            OSError,
            subprocess.SubprocessError,
            ValueError,
            KeyError,
            TypeError
        ) as error:
            print(f"[WARNING] Extended CPU telemetry unavailable: {error}")

    print(f"Student ID: {student_id}")
    print(f"Processor : {processor}")
    print(f"OS        : {platform.system()} {platform.release()}")
    print(f"OS Version: {platform.version()}")
    print(f"Physical Cores : {physical_cores}")
    print(f"CPU Count : {logical_cores} Logical Cores")
    print(f"N Elements: {N_ELEMENTS}")
    print(f"Num Items : {NUM_ITEMS}")
