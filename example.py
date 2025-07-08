"""
Example usage of the debug_utils package for AI/ML debugging workflows.

This example demonstrates various ways to use the debugging utilities
to capture function calls, serialize complex objects, and generate test scripts.
"""

import torch
import numpy as np
from debug_utils import (
    capture_function, 
    capture_and_generate_script,
    save_debug_session,
    quick_debug_capture,
    benchmark_function_performance,
    setup_debug_environment
)


# Example 1: Basic function decoration
@capture_function()
def simple_computation(x, y, operation="add"):
    """Simple computation function for demonstration."""
    if operation == "add":
        return x + y
    elif operation == "multiply":
        return x * y
    elif operation == "divide":
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y
    else:
        raise ValueError(f"Unknown operation: {operation}")


# Example 2: AI/ML model function with complex objects
@capture_function()
def model_forward_pass(input_tensor, model_weights, config):
    """Simulate a model forward pass with tensors."""
    # Simulate some tensor operations
    hidden = torch.matmul(input_tensor, model_weights['linear1'])
    hidden = torch.relu(hidden)
    
    if config.get('use_dropout', False):
        hidden = torch.dropout(hidden, p=config.get('dropout_rate', 0.5))
    
    output = torch.matmul(hidden, model_weights['linear2'])
    
    if config.get('apply_softmax', False):
        output = torch.softmax(output, dim=-1)
    
    return output


# Example 3: Function that might fail
@capture_function()
def risky_computation(data, threshold=0.5):
    """Function that might fail based on input conditions."""
    if not isinstance(data, (list, np.ndarray, torch.Tensor)):
        raise TypeError("Data must be a list, numpy array, or torch tensor")
    
    if hasattr(data, 'mean'):
        mean_val = data.mean()
    else:
        mean_val = sum(data) / len(data)
    
    if mean_val < threshold:
        raise ValueError(f"Mean value {mean_val} below threshold {threshold}")
    
    return mean_val * 2


def demonstrate_basic_usage():
    """Demonstrate basic debugging workflow."""
    print("=== Basic Usage Demo ===\n")
    
    # Run some functions with the capture decorator
    print("Running captured functions...")
    
    # Successful calls
    result1 = simple_computation(5, 3, "add")
    result2 = simple_computation(4, 7, "multiply")
    
    # Call with tensor operations
    input_tensor = torch.randn(10, 5)
    weights = {
        'linear1': torch.randn(5, 8),
        'linear2': torch.randn(8, 3)
    }
    config = {'use_dropout': False, 'apply_softmax': True}
    model_result = model_forward_pass(input_tensor, weights, config)
    
    # Try a risky computation that should succeed
    good_data = np.array([0.8, 0.9, 0.7, 0.6])
    risk_result = risky_computation(good_data, threshold=0.5)
    
    # Try a risky computation that should fail
    try:
        bad_data = np.array([0.1, 0.2, 0.3])
        risky_computation(bad_data, threshold=0.5)
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    print("All function calls captured!")


def demonstrate_script_generation():
    """Demonstrate generating test scripts from captures."""
    print("\n=== Script Generation Demo ===\n")
    
    # Generate a test script for a specific function call
    print("Generating test script for tensor computation...")
    
    input_tensor = torch.randn(5, 3)
    weights = {
        'linear1': torch.randn(3, 4),
        'linear2': torch.randn(4, 2)
    }
    config = {'use_dropout': True, 'dropout_rate': 0.3}
    
    script_path = capture_and_generate_script(
        model_forward_pass,
        args=(input_tensor, weights, config),
        output_dir="./debug_output",
        script_name="test_model_forward.py"
    )
    
    print(f"Generated script: {script_path}")


def demonstrate_session_management():
    """Demonstrate saving and managing debug sessions."""
    print("\n=== Session Management Demo ===\n")
    
    # Run several more functions to build up a session
    simple_computation(10, 5, "divide")
    simple_computation(8, 4, "multiply")
    
    # Try some operations that will fail
    try:
        simple_computation(10, 0, "divide")
    except ValueError:
        pass
    
    try:
        simple_computation(5, 3, "invalid_op")
    except ValueError:
        pass
    
    # Save the entire debug session
    session_path = save_debug_session(
        output_dir="./debug_session_example",
        include_scripts=True,
        clear_after_save=False
    )
    
    print(f"Saved debug session to: {session_path}")


def demonstrate_quick_capture():
    """Demonstrate quick capture for one-off debugging."""
    print("\n=== Quick Capture Demo ===\n")
    
    # Quick capture without decorator
    def problematic_function(x, y):
        if x > y:
            return x / (x - y)
        else:
            raise ValueError("x must be greater than y")
    
    # Capture a successful call
    call1 = quick_debug_capture(problematic_function, 10, 3)
    print(f"Captured successful call: {call1.function_name}")
    
    # Capture a failed call
    call2 = quick_debug_capture(problematic_function, 3, 10)
    print(f"Captured failed call: {call2.function_name}")
    print(f"Error captured: {call2.error_type}")


def demonstrate_performance_benchmarking():
    """Demonstrate performance benchmarking with capture."""
    print("\n=== Performance Benchmarking Demo ===\n")
    
    def expensive_operation(size):
        """Simulate an expensive computation."""
        data = torch.randn(size, size)
        result = torch.matmul(data, data.T)
        return torch.sum(result)
    
    # Benchmark the function
    stats = benchmark_function_performance(
        expensive_operation,
        args=(100,),
        num_runs=5
    )
    
    print("Performance stats:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")


def main():
    """Run all demonstration examples."""
    print("Debug Utils Package Demonstration")
    print("=" * 50)
    
    # Set up a clean debug environment
    workspace = setup_debug_environment()
    
    # Run all demonstrations
    demonstrate_basic_usage()
    demonstrate_script_generation()
    demonstrate_session_management()
    demonstrate_quick_capture()
    demonstrate_performance_benchmarking()
    
    print(f"\n=== Demo Complete ===")
    print(f"All debug artifacts saved in: {workspace}")
    print("\nNext steps:")
    print("1. Check the generated test scripts in workspace/scripts/")
    print("2. Review captured data in workspace/sessions/")
    print("3. Run the generated test scripts independently for debugging")


if __name__ == "__main__":
    main()

