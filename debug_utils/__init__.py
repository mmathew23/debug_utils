"""
Debug Utilities Package for AI Training and Inference

A modular toolkit for capturing function calls, serializing complex objects,
and generating standalone test scripts for debugging AI/ML workflows.

Key Features:
- Function call capture with automatic serialization
- Support for PyTorch tensors, NumPy arrays, and complex objects
- Standalone test script generation
- Batch testing capabilities
- Debug session management

Basic Usage:
    # Capture a function call
    from debug_utils import capture_function
    
    @capture_function()
    def my_model_function(tensor, config):
        # Your model code here
        return result
    
    # Generate test script from captured calls
    from debug_utils import save_debug_session
    save_debug_session("./my_debug_session")
    
    # Quick capture and script generation
    from debug_utils import capture_and_generate_script
    capture_and_generate_script(my_function, args=(arg1, arg2), kwargs={'param': value})
"""

# Core capture functionality
from .capture import (
    FunctionCall,
    FunctionCapture,
    capture_function,
    get_captured_calls,
    clear_captured_calls,
    default_capture,
    instrument_method,
    uninstrument_method,
    capture_method,
)

# Serialization utilities
from .serialization import (
    serialize_object,
    deserialize_object,
    serialize_function_args,
    deserialize_function_args,
    SerializationError
)

# Script generation
from .script_generator import (
    generate_test_script,
    generate_batch_test_script
)

# High-level utilities
from .utils import (
    quick_debug_capture,
    capture_and_generate_script,
    save_debug_session,
    load_debug_session,
    compare_function_outputs,
    benchmark_function_performance,
    create_debug_workspace
)

from .environment import (
    get_environment_info,
    get_python_info,
    get_torch_info,
    get_process_info,
)

# Version info
__version__ = "0.1.0"
__author__ = "AI Debug Utils"

# Public API
__all__ = [
    # Core capture
    "FunctionCall",
    "FunctionCapture", 
    "capture_function",
    "get_captured_calls",
    "clear_captured_calls",
    "default_capture",
    
    # Serialization
    "serialize_object",
    "deserialize_object", 
    "serialize_function_args",
    "deserialize_function_args",
    "SerializationError",
    
    # Script generation
    "generate_test_script",
    "generate_batch_test_script",
    
    # High-level utilities
    "quick_debug_capture",
    "capture_and_generate_script",
    "save_debug_session", 
    "load_debug_session",
    "compare_function_outputs",
    "benchmark_function_performance",
    "create_debug_workspace"
]


def setup_debug_environment():
    """
    Set up a complete debugging environment with workspace and basic configuration.
    
    Returns:
        Path to the created workspace
    """
    workspace = create_debug_workspace()
    print(f"Debug environment ready at {workspace}")
    print("\nQuick start:")
    print("1. Use @capture_function() decorator on functions you want to debug")
    print("2. Run your code and let it capture function calls")
    print("3. Use save_debug_session() to save captured data and generate test scripts")
    print("4. Find generated scripts in the workspace/scripts directory")
    return workspace


def get_debug_stats():
    """Get statistics about current debug session."""
    calls = get_captured_calls()
    
    if not calls:
        return {"message": "No captured calls in current session"}
    
    stats = {
        "total_calls": len(calls),
        "unique_functions": len(set(call.function_name for call in calls)),
        "successful_calls": len([call for call in calls if call.error is None]),
        "failed_calls": len([call for call in calls if call.error is not None]),
        "functions": list(set(call.function_name for call in calls)),
        "latest_call": calls[-1].timestamp if calls else None
    }
    
    return stats


# Convenience aliases for common workflows
capture = capture_function  # Shorter alias
quick_capture = quick_debug_capture  # Alternative name
save_session = save_debug_session  # Shorter alias
load_session = load_debug_session  # Shorter alias
