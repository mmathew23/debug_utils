"""Environment and system information utilities."""
from __future__ import annotations
import sys
import os
import platform
from datetime import datetime
from typing import Any, Dict, List


def get_python_info() -> Dict[str, Any]:
    """Return basic Python environment information."""
    return {
        "version": sys.version,
        "executable": sys.executable,
        "platform": sys.platform,
        "implementation": platform.python_implementation(),
    }


def get_torch_info() -> Dict[str, Any]:
    """Return PyTorch installation and GPU info if available."""
    info: Dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        info["available"] = True
        info["version"] = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            devices: List[Dict[str, Any]] = []
            for idx in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(idx)
                devices.append({
                    "id": idx,
                    "name": props.name,
                    "total_memory": props.total_memory,
                })
            info["devices"] = devices
    except Exception as e:  # pragma: no cover - optional dependency
        info["error"] = str(e)
    return info


def get_process_info() -> Dict[str, Any]:
    """Return simple process metrics."""
    info = {"pid": os.getpid()}
    try:
        import psutil  # type: ignore

        p = psutil.Process()
        info.update({
            "memory_mb": p.memory_info().rss / (1024 ** 2),
            "cpu_percent": p.cpu_percent(interval=0.0),
        })
    except Exception:
        pass
    return info


def get_environment_info() -> Dict[str, Any]:
    """Gather overall environment information."""
    return {
        "timestamp": datetime.now().isoformat(),
        "python": get_python_info(),
        "torch": get_torch_info(),
        "process": get_process_info(),
    }

