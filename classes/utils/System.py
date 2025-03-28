from os import getpid
from psutil import Process, virtual_memory

def checkMemory():
    pid = getpid()
    python_process = Process(pid)
    memoryUse = python_process.memory_info()[0]/2.**30  # memory use in GB...I think
    print('memory use:', memoryUse)

def get_available_memory():
    # Ottieni le informazioni sulla memoria
    memory_info = virtual_memory()

    # Memoria disponibile in byte
    available_memory = memory_info.available

    # Converti in megabyte (MB) o gigabyte (GB) se necessario
    available_memory_mb = available_memory / (1024 ** 2)
    available_memory_gb = available_memory / (1024 ** 3)

    return available_memory, available_memory_mb, available_memory_gb
