"""
Utility functions for debug capture and script generation.

This module provides convenient high-level functions for common debugging workflows.
"""

import json
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable, Union
from .capture import FunctionCall, default_capture, capture_function
from .script_generator import generate_test_script, generate_batch_test_script
from .serialization import serialize_function_args, deserialize_function_args


def quick_debug_capture(func: Callable, *args, **kwargs) -> FunctionCall:
    """
    Quickly capture a single function call for debugging.
    
    Args:
        func: Function to capture
        *args: Arguments to pass to function
        **kwargs: Keyword arguments to pass to function
    
    Returns:
        FunctionCall object with captured data
    """
    # Clear previous captures
    default_capture.clear_calls()
    
    # Decorate and call the function
    decorated_func = capture_function()(func)
    
    try:
        decorated_func(*args, **kwargs)
    except Exception:
        # We still want to capture failed calls
        pass
    
    # Return the captured call
    calls = default_capture.get_calls()
    return calls[0] if calls else None


def capture_and_generate_script(
    func: Callable,
    args: tuple = (),
    kwargs: Optional[Dict] = None,
    output_dir: Union[str, Path] = "./debug_output",
    script_name: Optional[str] = None
) -> Path:
    """
    Capture a function call and immediately generate a test script.
    
    Args:
        func: Function to capture
        args: Arguments tuple
        kwargs: Keyword arguments dict
        output_dir: Directory to save the script
        script_name: Name for the script file (auto-generated if None)
    
    Returns:
        Path to the generated script
    """
    if kwargs is None:
        kwargs = {}
    
    # Capture the call
    captured_call = quick_debug_capture(func, *args, **kwargs)
    
    if not captured_call:
        raise RuntimeError("Failed to capture function call")
    
    # Generate script
    output_dir = Path(output_dir)
    if script_name is None:
        script_name = f"test_{captured_call.function_name}_{captured_call.id[:8]}.py"
    
    script_path = output_dir / script_name
    generate_test_script(captured_call, script_path)
    
    print(f"Generated test script: {script_path}")
    return script_path


def save_debug_session(
    output_dir: Union[str, Path] = "./debug_session",
    include_scripts: bool = True,
    clear_after_save: bool = False
) -> Path:
    """
    Save all captured calls from the current session.
    
    Args:
        output_dir: Directory to save session data
        include_scripts: Whether to generate test scripts
        clear_after_save: Whether to clear captures after saving
    
    Returns:
        Path to the session directory
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    calls = default_capture.get_calls()
    
    if not calls:
        print("No captured calls to save")
        return output_dir
    
    # Save raw capture data
    calls_data = [call.to_dict() for call in calls]
    with open(output_dir / "captured_calls.json", 'w') as f:
        json.dump(calls_data, f, indent=2, default=str)
    
    # Generate individual test scripts
    if include_scripts:
        scripts_dir = output_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        for call in calls:
            script_name = f"test_{call.function_name}_{call.id[:8]}.py"
            generate_test_script(call, scripts_dir / script_name)
        
        # Generate batch script
        batch_script_path = scripts_dir / "test_all.py"
        generate_batch_test_script(calls, batch_script_path)
        
        print(f"Generated {len(calls)} individual test scripts and 1 batch script")
    
    # Create session summary
    summary = {
        "total_calls": len(calls),
        "functions": list(set(call.function_name for call in calls)),
        "successful_calls": len([call for call in calls if call.error is None]),
        "failed_calls": len([call for call in calls if call.error is not None]),
        "session_saved_at": calls[-1].timestamp if calls else None
    }
    
    with open(output_dir / "session_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Saved debug session to {output_dir}")
    print(f"Summary: {summary['total_calls']} calls, {summary['successful_calls']} successful, {summary['failed_calls']} failed")
    
    if clear_after_save:
        default_capture.clear_calls()
        print("Cleared captured calls")
    
    return output_dir


def load_debug_session(session_dir: Union[str, Path]) -> List[FunctionCall]:
    """
    Load a previously saved debug session.
    
    Args:
        session_dir: Path to session directory
    
    Returns:
        List of loaded FunctionCall objects
    """
    session_dir = Path(session_dir)
    calls_file = session_dir / "captured_calls.json"
    
    if not calls_file.exists():
        raise FileNotFoundError(f"No captured calls found in {session_dir}")
    
    with open(calls_file, 'r') as f:
        calls_data = json.load(f)
    
    # Reconstruct FunctionCall objects
    calls = []
    for call_data in calls_data:
        call = FunctionCall(**call_data)
        calls.append(call)
    
    print(f"Loaded {len(calls)} captured calls from {session_dir}")
    return calls


def compare_function_outputs(call1: FunctionCall, call2: FunctionCall) -> Dict[str, Any]:
    """
    Compare outputs from two function calls.
    
    Args:
        call1: First function call
        call2: Second function call
    
    Returns:
        Comparison results dictionary
    """
    comparison = {
        "functions_match": call1.function_name == call2.function_name,
        "both_successful": call1.error is None and call2.error is None,
        "both_failed": call1.error is not None and call2.error is not None,
        "outputs_equal": False,
        "output_types_match": False,
        "notes": []
    }
    
    if not comparison["functions_match"]:
        comparison["notes"].append(f"Different functions: {call1.function_name} vs {call2.function_name}")
    
    if comparison["both_successful"]:
        try:
            comparison["outputs_equal"] = call1.output == call2.output
            comparison["output_types_match"] = type(call1.output) == type(call2.output)
        except Exception as e:
            comparison["notes"].append(f"Could not compare outputs: {e}")
    
    elif comparison["both_failed"]:
        comparison["error_types_match"] = call1.error_type == call2.error_type
        comparison["notes"].append("Both calls failed")
    
    else:
        comparison["notes"].append("One call succeeded, one failed")
    
    return comparison


def benchmark_function_performance(
    func: Callable,
    args: tuple = (),
    kwargs: Optional[Dict] = None,
    num_runs: int = 10
) -> Dict[str, Any]:
    """
    Benchmark a function and capture performance data.
    
    Args:
        func: Function to benchmark
        args: Arguments tuple
        kwargs: Keyword arguments dict
        num_runs: Number of runs for benchmarking
    
    Returns:
        Performance statistics
    """
    import time
    
    if kwargs is None:
        kwargs = {}
    
    # Clear previous captures
    default_capture.clear_calls()
    
    decorated_func = capture_function()(func)
    
    times = []
    successful_runs = 0
    
    for i in range(num_runs):
        start_time = time.time()
        try:
            decorated_func(*args, **kwargs)
            successful_runs += 1
        except Exception:
            pass  # We still capture failed calls
        end_time = time.time()
        times.append(end_time - start_time)
    
    calls = default_capture.get_calls()
    
    stats = {
        "function_name": func.__name__,
        "num_runs": num_runs,
        "successful_runs": successful_runs,
        "failed_runs": num_runs - successful_runs,
        "min_time": min(times),
        "max_time": max(times),
        "avg_time": sum(times) / len(times),
        "total_time": sum(times),
        "captured_calls": len(calls)
    }
    
    return stats


def create_debug_workspace(workspace_dir: Union[str, Path] = "./debug_workspace") -> Path:
    """
    Create a structured workspace for debugging sessions.
    
    Args:
        workspace_dir: Directory for the workspace
    
    Returns:
        Path to created workspace
    """
    workspace_dir = Path(workspace_dir)
    
    # Create directory structure
    dirs_to_create = [
        workspace_dir,
        workspace_dir / "sessions",
        workspace_dir / "scripts",
        workspace_dir / "data",
        workspace_dir / "reports"
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create README
    readme_content = """# Debug Workspace

This workspace contains debugging sessions and generated test scripts.

## Structure:
- `sessions/`: Saved debug sessions with captured function calls
- `scripts/`: Generated test scripts for reproducing issues
- `data/`: Serialized data files for complex objects
- `reports/`: Analysis reports and summaries

## Usage:
1. Use the debug capture utilities to capture problematic function calls
2. Generate test scripts for isolated debugging
3. Save sessions for later analysis
4. Compare function outputs across different runs
"""
    
    with open(workspace_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    print(f"Created debug workspace at {workspace_dir}")
    return workspace_dir

