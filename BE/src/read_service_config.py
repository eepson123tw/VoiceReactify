import psutil
import platform
import torch
from pydantic import BaseModel
import time

class SystemCheckResponse(BaseModel):
    cpu_count: int
    total_memory_gb: float
    free_disk_space_gb: float
    os_info: str
    has_gpu: bool
    is_compatible: bool

def get_average_value(function, samples=5, delay=0.1):
    values = []
    for _ in range(samples):
        values.append(function())
        time.sleep(delay)  # 延遲一點時間，讓系統有機會做其他工作
    return sum(values) / len(values)

def check_system_resources(samples=2):
    # 平均 CPU 頻率
    cpu_count = psutil.cpu_count(logical=False)
    # 平均 RAM
    total_memory = get_average_value(lambda: psutil.virtual_memory().total / (1024 ** 3), samples=samples)  # 轉換成 GB

    # 平均磁碟空間
    disk_space = get_average_value(lambda: psutil.disk_usage('/').free / (1024 ** 3), samples=samples)  # 轉換成 GB

    # 作業系統類型
    os_info = platform.system()

    # 檢查是否有 GPU（如果需要 GPU 支援）
    has_gpu = torch.cuda.is_available()

    # 根據條件檢查是否符合要求
    is_compatible = (
        cpu_count >= 4 and  # 至少4個核心
        total_memory >= 16 and  # 至少16GB RAM
        disk_space >= 50 and  # 至少50GB可用磁碟空間
        (os_info == "Linux" or os_info == "Windows") and  # 僅支援 Linux 和 Windows
        has_gpu  # 檢查是否有 GPU
    )

    return SystemCheckResponse(
        cpu_count=cpu_count,
        total_memory_gb=total_memory,
        free_disk_space_gb=disk_space,
        os_info=os_info,
        has_gpu=has_gpu,
        is_compatible=is_compatible
    )

