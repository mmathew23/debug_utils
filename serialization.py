"""
Serialization utilities for AI debugging.

Handles serialization and deserialization of complex objects commonly found
in AI/ML workflows, including tensors, models, and other specialized objects.
"""

import pickle
import json
import base64
import numpy as np
from typing import Any, Dict, Union, Optional
from pathlib import Path
import warnings


class SerializationError(Exception):
    """Raised when serialization/deserialization fails."""
    pass


def serialize_object(obj: Any, method: str = "auto") -> Dict[str, Any]:
    """
    Serialize an object to a dictionary format suitable for JSON storage.
    
    Args:
        obj: Object to serialize
        method: Serialization method ("auto", "pickle", "json", "numpy", "torch")
    
    Returns:
        Dictionary with serialized data and metadata
    """
    if method == "auto":
        method = _detect_serialization_method(obj)
    
    try:
        if method == "torch":
            return _serialize_torch_tensor(obj)
        elif method == "numpy":
            return _serialize_numpy_array(obj)
        elif method == "json":
            return _serialize_json_compatible(obj)
        elif method == "pickle":
            return _serialize_pickle(obj)
        else:
            # Fallback to pickle
            return _serialize_pickle(obj)
    except Exception as e:
        raise SerializationError(f"Failed to serialize object with method {method}: {e}")


def deserialize_object(data: Dict[str, Any]) -> Any:
    """
    Deserialize an object from a dictionary format.
    
    Args:
        data: Dictionary containing serialized data and metadata
    
    Returns:
        Deserialized object
    """
    method = data.get("method", "pickle")
    
    try:
        if method == "torch":
            return _deserialize_torch_tensor(data)
        elif method == "numpy":
            return _deserialize_numpy_array(data)
        elif method == "json":
            return data["data"]
        elif method == "pickle":
            return _deserialize_pickle(data)
        else:
            raise SerializationError(f"Unknown deserialization method: {method}")
    except Exception as e:
        raise SerializationError(f"Failed to deserialize object with method {method}: {e}")


def _detect_serialization_method(obj: Any) -> str:
    """Detect the best serialization method for an object."""
    # Check for torch tensors
    if hasattr(obj, '__class__') and 'torch' in str(type(obj)):
        return "torch"
    
    # Check for numpy arrays
    if isinstance(obj, np.ndarray):
        return "numpy"
    
    # Check if JSON-serializable
    try:
        json.dumps(obj)
        return "json"
    except (TypeError, ValueError):
        pass
    
    # Fallback to pickle
    return "pickle"


def _serialize_torch_tensor(tensor) -> Dict[str, Any]:
    """Serialize a PyTorch tensor."""
    try:
        import torch
        
        if not isinstance(tensor, torch.Tensor):
            raise ValueError("Object is not a PyTorch tensor")
        
        # Convert to numpy and then serialize
        numpy_array = tensor.detach().cpu().numpy()
        return {
            "method": "torch",
            "data": base64.b64encode(numpy_array.tobytes()).decode('utf-8'),
            "dtype": str(numpy_array.dtype),
            "shape": list(numpy_array.shape),
            "device": str(tensor.device),
            "requires_grad": tensor.requires_grad
        }
    except ImportError:
        raise SerializationError("PyTorch not available for tensor serialization")


def _deserialize_torch_tensor(data: Dict[str, Any]):
    """Deserialize a PyTorch tensor."""
    try:
        import torch
        
        # Reconstruct numpy array
        array_bytes = base64.b64decode(data["data"])
        numpy_array = np.frombuffer(array_bytes, dtype=data["dtype"]).reshape(data["shape"])
        
        # Convert to torch tensor
        tensor = torch.from_numpy(numpy_array.copy())
        
        # Move to device and set requires_grad
        if data.get("device", "cpu") != "cpu":
            tensor = tensor.to(data["device"])
        
        if data.get("requires_grad", False):
            tensor.requires_grad_(True)
        
        return tensor
    except ImportError:
        raise SerializationError("PyTorch not available for tensor deserialization")


def _serialize_numpy_array(array: np.ndarray) -> Dict[str, Any]:
    """Serialize a numpy array."""
    return {
        "method": "numpy",
        "data": base64.b64encode(array.tobytes()).decode('utf-8'),
        "dtype": str(array.dtype),
        "shape": list(array.shape)
    }


def _deserialize_numpy_array(data: Dict[str, Any]) -> np.ndarray:
    """Deserialize a numpy array."""
    array_bytes = base64.b64decode(data["data"])
    return np.frombuffer(array_bytes, dtype=data["dtype"]).reshape(data["shape"])


def _serialize_json_compatible(obj: Any) -> Dict[str, Any]:
    """Serialize JSON-compatible objects."""
    return {
        "method": "json",
        "data": obj
    }


def _serialize_pickle(obj: Any) -> Dict[str, Any]:
    """Serialize using pickle (fallback method)."""
    pickled_data = pickle.dumps(obj)
    return {
        "method": "pickle",
        "data": base64.b64encode(pickled_data).decode('utf-8'),
        "type": str(type(obj))
    }


def _deserialize_pickle(data: Dict[str, Any]) -> Any:
    """Deserialize using pickle."""
    pickled_bytes = base64.b64decode(data["data"])
    return pickle.loads(pickled_bytes)


def serialize_function_args(args: tuple, kwargs: dict) -> Dict[str, Any]:
    """
    Serialize function arguments.
    
    Args:
        args: Positional arguments tuple
        kwargs: Keyword arguments dictionary
    
    Returns:
        Dictionary with serialized arguments
    """
    serialized_args = []
    serialized_kwargs = {}
    
    # Serialize positional arguments
    for i, arg in enumerate(args):
        try:
            serialized_args.append(serialize_object(arg))
        except SerializationError as e:
            warnings.warn(f"Failed to serialize arg {i}: {e}")
            serialized_args.append({
                "method": "failed",
                "error": str(e),
                "type": str(type(arg)),
                "repr": repr(arg)
            })
    
    # Serialize keyword arguments
    for key, value in kwargs.items():
        try:
            serialized_kwargs[key] = serialize_object(value)
        except SerializationError as e:
            warnings.warn(f"Failed to serialize kwarg {key}: {e}")
            serialized_kwargs[key] = {
                "method": "failed",
                "error": str(e),
                "type": str(type(value)),
                "repr": repr(value)
            }
    
    return {
        "args": serialized_args,
        "kwargs": serialized_kwargs
    }


def deserialize_function_args(data: Dict[str, Any]) -> tuple:
    """
    Deserialize function arguments.
    
    Args:
        data: Dictionary with serialized arguments
    
    Returns:
        Tuple of (args, kwargs)
    """
    args = []
    kwargs = {}
    
    # Deserialize positional arguments
    for arg_data in data.get("args", []):
        if arg_data.get("method") == "failed":
            # Create a placeholder for failed serialization
            args.append(f"<FAILED_SERIALIZATION: {arg_data.get('type', 'unknown')}>")
        else:
            try:
                args.append(deserialize_object(arg_data))
            except SerializationError:
                args.append(f"<DESERIALIZATION_ERROR: {arg_data.get('type', 'unknown')}>")
    
    # Deserialize keyword arguments
    for key, kwarg_data in data.get("kwargs", {}).items():
        if kwarg_data.get("method") == "failed":
            kwargs[key] = f"<FAILED_SERIALIZATION: {kwarg_data.get('type', 'unknown')}>"
        else:
            try:
                kwargs[key] = deserialize_object(kwarg_data)
            except SerializationError:
                kwargs[key] = f"<DESERIALIZATION_ERROR: {kwarg_data.get('type', 'unknown')}>"
    
    return tuple(args), kwargs


def create_placeholder_for_complex_object(obj: Any) -> str:
    """Create a string placeholder for objects that can't be serialized."""
    return f"<PLACEHOLDER: {type(obj).__name__} at {hex(id(obj))}>"

