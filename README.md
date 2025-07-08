# Debug Utils for AI Training and Inference

A modular Python package for debugging AI/ML workflows by capturing function calls, serializing complex objects, and generating standalone test scripts.

## Features

- **Function Call Capture**: Automatically capture function inputs, outputs, and errors using decorators
- **Complex Object Serialization**: Handle PyTorch tensors, NumPy arrays, and other AI/ML objects
- **Standalone Script Generation**: Create executable test scripts for isolated debugging
- **Session Management**: Save and load debug sessions for later analysis
- **Performance Benchmarking**: Measure function performance while capturing calls
- **Modular Design**: Use individual components or the complete workflow

## Quick Start

```python
from debug_utils import capture_function, save_debug_session

# Decorate functions you want to debug
@capture_function()
def my_model_function(input_tensor, weights, config):
    # Your AI/ML code here
    output = torch.matmul(input_tensor, weights)
    return torch.relu(output)

# Run your code normally
result = my_model_function(my_tensor, my_weights, my_config)

# Save captured calls and generate test scripts
save_debug_session("./my_debug_session")
```

## Installation

```bash
# Clone or copy the debug_utils package to your project
# Install dependencies
pip install torch numpy pandas
```

## Package Structure

```
debug_utils/
├── __init__.py          # Main package interface
├── capture.py           # Function call capture and instrumentation
├── serialization.py     # Object serialization for complex AI objects
├── script_generator.py  # Standalone test script generation
└── utils.py            # High-level convenience functions
```

## Core Components

### 1. Function Capture (`capture.py`)

Capture function calls with their inputs, outputs, and any errors:

```python
from debug_utils import capture_function, get_captured_calls

@capture_function()
def problematic_function(x, y):
    if x > 0:
        return x / y
    else:
        raise ValueError("x must be positive")

# Calls are automatically captured
result = problematic_function(10, 2)

# Access captured calls
calls = get_captured_calls()
print(f"Captured {len(calls)} calls")
```

### 2. Object Serialization (`serialization.py`)

Handle complex AI/ML objects like tensors and models:

```python
from debug_utils import serialize_object, deserialize_object
import torch

# Serialize a PyTorch tensor
tensor = torch.randn(3, 4)
serialized = serialize_object(tensor)

# Deserialize back to tensor
restored_tensor = deserialize_object(serialized)
```

### 3. Script Generation (`script_generator.py`)

Generate standalone test scripts from captured calls:

```python
from debug_utils import generate_test_script, get_captured_calls

# After capturing some calls
calls = get_captured_calls()
script_content = generate_test_script(calls[0], output_path="test_script.py")
```

### 4. High-Level Utilities (`utils.py`)

Convenient functions for common workflows:

```python
from debug_utils import capture_and_generate_script, benchmark_function_performance

# Quick capture and script generation
script_path = capture_and_generate_script(
    my_function, 
    args=(arg1, arg2), 
    kwargs={'param': value}
)

# Performance benchmarking with capture
stats = benchmark_function_performance(expensive_function, num_runs=10)
```

## Common Workflows

### Debugging a Single Function

```python
from debug_utils import quick_debug_capture, generate_test_script

def buggy_function(data, threshold=0.5):
    # Some complex AI logic that sometimes fails
    processed = preprocess(data)
    result = model.forward(processed)
    if result.mean() < threshold:
        raise ValueError("Result below threshold")
    return result

# Capture the problematic call
call = quick_debug_capture(buggy_function, problematic_data, threshold=0.3)

# Generate a test script
generate_test_script(call, "debug_buggy_function.py")
```

### Session-Based Debugging

```python
from debug_utils import capture_function, save_debug_session

# Decorate multiple functions
@capture_function()
def preprocess_data(raw_data):
    return clean_and_normalize(raw_data)

@capture_function()
def run_model(processed_data, model_config):
    return model.predict(processed_data, **model_config)

@capture_function()
def postprocess_results(predictions, output_format):
    return format_predictions(predictions, output_format)

# Run your pipeline - all calls are captured automatically
data = load_data()
processed = preprocess_data(data)
predictions = run_model(processed, config)
results = postprocess_results(predictions, "json")

# Save everything for later analysis
save_debug_session("./pipeline_debug_session")
```

### Working with Complex Objects

The package automatically handles serialization of:
- PyTorch tensors (with device, dtype, and grad info)
- NumPy arrays
- Standard Python objects (lists, dicts, etc.)
- Custom objects (via pickle fallback)

```python
@capture_function()
def complex_model_function(
    input_tensor,      # torch.Tensor
    model_weights,     # Dict of tensors
    numpy_features,    # np.ndarray
    config             # Dict with mixed types
):
    # All arguments will be automatically serialized
    return model.forward(input_tensor, model_weights, numpy_features, **config)
```

## Generated Test Scripts

The package generates standalone Python scripts that:
- Import all necessary modules
- Recreate the function and its arguments
- Execute the function call
- Compare outputs (when available)
- Handle both successful and failed calls

Example generated script structure:
```python
"""
Test script for captured function call: model_forward_pass
Generated from call ID: abc123ef
"""

import torch
import numpy as np
# ... other imports

def model_forward_pass(input_tensor, weights, config):
    # Original function code or import

# Load test data
args_data = {...}  # Serialized arguments
expected_output = {...}  # Expected result

def run_test():
    result = model_forward_pass(*args, **kwargs)
    # Validation logic
    return True

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
```

## Advanced Features

### Custom Serialization

Extend serialization for custom objects:

```python
from debug_utils.serialization import serialize_object

# The serialization system will try multiple methods:
# 1. PyTorch tensor serialization
# 2. NumPy array serialization  
# 3. JSON-compatible objects
# 4. Pickle fallback
```

### Performance Monitoring

```python
from debug_utils import benchmark_function_performance

stats = benchmark_function_performance(
    expensive_function,
    args=(large_tensor,),
    num_runs=10
)

print(f"Average time: {stats['avg_time']:.4f}s")
print(f"Success rate: {stats['successful_runs']}/{stats['num_runs']}")
```

### Method Instrumentation

Capture methods of classes or models on the fly:

```python
from debug_utils import capture_method
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained('gpt2')

# Temporarily capture forward pass
with capture_method(model, 'forward'):
    model(torch.randint(0, 10, (1, 5)))

# Retrieve captured call
call = get_captured_calls()[-1]
print(call.function_name, call.error)
```

### Workspace Management

```python
from debug_utils import create_debug_workspace, setup_debug_environment

# Create organized workspace
workspace = create_debug_workspace("./my_debug_workspace")

# Or set up complete environment
setup_debug_environment()
```

## Best Practices

1. **Use decorators during development**: Add `@capture_function()` to functions you're debugging
2. **Capture at the right level**: Focus on the specific function causing issues rather than decorating everything
3. **Save sessions regularly**: Use `save_debug_session()` after reproducing issues
4. **Test generated scripts**: Run the generated test scripts to verify they work independently
5. **Clean up captures**: Use `clear_captured_calls()` between different debugging sessions

## Error Handling

The package gracefully handles:
- Serialization failures (falls back to string representations)
- Import errors for optional dependencies
- Complex object types that can't be perfectly recreated
- Function calls that raise exceptions

## Dependencies

- **Required**: `numpy`, `json`, `pickle` (standard library)
- **Optional**: `torch` (for PyTorch tensor support)
- **Optional**: `pandas` (for DataFrame support)

## Contributing

This is designed as a modular toolkit. You can:
- Extend serialization support for new object types
- Add new script generation templates
- Implement custom capture strategies
- Add analysis and visualization tools

## License

AGPL-3
