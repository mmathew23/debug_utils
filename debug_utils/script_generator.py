"""
Script generation utilities for creating standalone test scripts from captured function calls.

This module generates executable Python scripts that can reproduce captured function calls
for debugging and testing purposes.
"""

import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from .capture import FunctionCall
from .serialization import serialize_function_args, serialize_object


def generate_test_script(
    call: FunctionCall,
    output_path: Optional[Path] = None,
    include_assertions: bool = True,
    save_data_separately: bool = True
) -> str:
    """
    Generate a standalone test script for a captured function call.
    
    Args:
        call: Captured function call
        output_path: Path where script will be saved (optional)
        include_assertions: Whether to include output assertions
        save_data_separately: Whether to save serialized data in separate files
    
    Returns:
        Generated script content as string
    """
    script_parts = []
    
    # Add header comment
    script_parts.append(_generate_header_comment(call))
    
    # Add imports
    script_parts.append(_generate_imports(call))
    
    # Add function definition if source is available
    if call.function_source:
        script_parts.append(_generate_function_definition(call))
    else:
        script_parts.append(_generate_function_import(call))
    
    # Add data loading section
    data_section, data_files = _generate_data_section(call, save_data_separately)
    script_parts.append(data_section)
    
    # Add test execution
    script_parts.append(_generate_test_execution(call, include_assertions))
    
    # Add main execution block
    script_parts.append(_generate_main_block())
    
    script_content = "\n\n".join(script_parts)
    
    # Save script if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(script_content)
        
        # Save data files if needed
        if save_data_separately and data_files:
            for filename, data in data_files.items():
                data_path = output_path.parent / filename
                with open(data_path, 'w') as f:
                    json.dump(data, f, indent=2)
    
    return script_content


def generate_batch_test_script(
    calls: List[FunctionCall],
    output_path: Optional[Path] = None,
    group_by_function: bool = True
) -> str:
    """
    Generate a test script for multiple captured function calls.
    
    Args:
        calls: List of captured function calls
        output_path: Path where script will be saved (optional)
        group_by_function: Whether to group tests by function name
    
    Returns:
        Generated script content as string
    """
    if not calls:
        return "# No function calls to generate tests for"
    
    script_parts = []
    
    # Add header
    script_parts.append(f'"""\nBatch test script for {len(calls)} captured function calls.\nGenerated automatically from debug captures.\n"""')
    
    # Collect all imports
    all_imports = set()
    for call in calls:
        if call.imports:
            all_imports.update(call.imports)
    
    # Add common imports
    all_imports.update([
        "import json",
        "import sys",
        "from pathlib import Path"
    ])
    
    script_parts.append("\n".join(sorted(all_imports)))
    
    if group_by_function:
        # Group calls by function name
        function_groups = {}
        for call in calls:
            if call.function_name not in function_groups:
                function_groups[call.function_name] = []
            function_groups[call.function_name].append(call)
        
        # Generate tests for each function group
        for func_name, func_calls in function_groups.items():
            script_parts.append(f"\n# Tests for {func_name}")
            for i, call in enumerate(func_calls):
                script_parts.append(_generate_single_test_function(call, f"test_{func_name}_{i}"))
    else:
        # Generate tests in chronological order
        for i, call in enumerate(calls):
            script_parts.append(_generate_single_test_function(call, f"test_call_{i}"))
    
    # Add main execution
    script_parts.append(_generate_batch_main_block(calls, group_by_function))
    
    script_content = "\n\n".join(script_parts)
    
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(script_content)
    
    return script_content


def _generate_header_comment(call: FunctionCall) -> str:
    """Generate header comment for the script."""
    return f'''"""
Test script for captured function call: {call.function_name}
Generated from call ID: {call.id}
Captured at: {call.timestamp}
Module: {call.module_name}

This script reproduces the captured function call for debugging purposes.
"""'''


def _generate_imports(call: FunctionCall) -> str:
    """Generate import statements."""
    imports = []
    
    # Add captured imports
    if call.imports:
        imports.extend(call.imports)
    
    # Add required imports for the script
    required_imports = [
        "import json",
        "import sys",
        "from pathlib import Path",
        "import traceback"
    ]
    
    imports.extend(required_imports)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_imports = []
    for imp in imports:
        if imp not in seen:
            seen.add(imp)
            unique_imports.append(imp)
    
    return "\n".join(unique_imports)


def _generate_function_definition(call: FunctionCall) -> str:
    """Generate function definition from captured source."""
    return f"# Function definition from captured source:\n{call.function_source}"


def _generate_function_import(call: FunctionCall) -> str:
    """Generate import statement for function when source not available."""
    return f"# Import the function (source not captured)\nfrom {call.module_name} import {call.function_name}"


def _generate_data_section(call: FunctionCall, save_separately: bool = True) -> tuple:
    """Generate data loading section and return any external data files."""
    data_files = {}
    
    if save_separately:
        # Save arguments in separate file
        args_data = serialize_function_args(call.args, call.kwargs)
        data_filename = f"{call.function_name}_{call.id[:8]}_args.json"
        data_files[data_filename] = args_data
        
        data_section = f'''# Load test data
script_dir = Path(__file__).parent
args_data = json.load(open(script_dir / "{data_filename}"))

# Deserialize arguments (note: complex objects may need manual reconstruction)
# You may need to import and use the serialization module for complex objects
args = args_data["args"]
kwargs = args_data["kwargs"]'''
        
        if call.output is not None:
            # Save expected output
            try:
                output_data = serialize_object(call.output)
                output_filename = f"{call.function_name}_{call.id[:8]}_output.json"
                data_files[output_filename] = output_data
                
                data_section += f'''
expected_output_data = json.load(open(script_dir / "{output_filename}"))
# Note: You may need to deserialize the expected output for comparison'''
            except Exception:
                data_section += "\n# Expected output could not be serialized"
    
    else:
        # Embed data directly in script
        args_data = serialize_function_args(call.args, call.kwargs)
        data_section = f'''# Test data (embedded)
args_data = {json.dumps(args_data, indent=2)}
args = args_data["args"]
kwargs = args_data["kwargs"]'''
        
        if call.output is not None:
            try:
                output_data = serialize_object(call.output)
                data_section += f'''
expected_output_data = {json.dumps(output_data, indent=2)}'''
            except Exception:
                data_section += "\n# Expected output could not be serialized"
    
    return data_section, data_files


def _generate_test_execution(call: FunctionCall, include_assertions: bool = True) -> str:
    """Generate the test execution code."""
    execution_code = f'''def run_test():
    """Run the captured function call test."""
    print(f"Testing {call.function_name}...")
    
    try:
        # Execute the function call
        # Note: You may need to manually reconstruct complex arguments
        result = {call.function_name}(*args, **kwargs)
        print("✓ Function executed successfully")
        print(f"Result type: {{type(result)}}")
        print(f"Result: {{result}}")'''
    
    if include_assertions and call.output is not None:
        execution_code += '''
        
        # Compare with expected output (basic comparison)
        # Note: For complex objects, you may need custom comparison logic
        if "expected_output_data" in globals():
            print("\\nComparing with expected output...")
            # Add your comparison logic here
            print("⚠ Manual comparison required for complex objects")'''
    
    if call.error:
        execution_code += f'''
        
    except Exception as e:
        print("✗ Function execution failed")
        print(f"Error: {{e}}")
        print("\\nExpected error (from capture):")
        print("""{call.error}""")
        
        # Check if error matches expected
        if isinstance(e, {call.error_type}):
            print("✓ Error type matches expected")
        else:
            print(f"✗ Error type mismatch. Expected {call.error_type}, got {{type(e).__name__}}")
        
        traceback.print_exc()'''
    else:
        execution_code += '''
        
    except Exception as e:
        print("✗ Unexpected error occurred")
        print(f"Error: {e}")
        traceback.print_exc()
        return False
    
    return True'''
    
    return execution_code


def _generate_main_block() -> str:
    """Generate main execution block."""
    return '''if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)'''


def _generate_single_test_function(call: FunctionCall, test_name: str) -> str:
    """Generate a single test function for batch testing."""
    return f'''def {test_name}():
    """Test for {call.function_name} (ID: {call.id[:8]})"""
    print(f"Running {test_name}...")
    # TODO: Implement test logic for this call
    # Call captured at: {call.timestamp}
    pass'''


def _generate_batch_main_block(calls: List[FunctionCall], group_by_function: bool) -> str:
    """Generate main block for batch testing."""
    if group_by_function:
        # Group test names by function
        function_groups = {}
        for i, call in enumerate(calls):
            if call.function_name not in function_groups:
                function_groups[call.function_name] = []
            function_groups[call.function_name].append(f"test_{call.function_name}_{len(function_groups.get(call.function_name, []))}")
        
        test_calls = []
        for func_name, test_names in function_groups.items():
            test_calls.extend(test_names)
    else:
        test_calls = [f"test_call_{i}" for i in range(len(calls))]
    
    test_list = ",\n        ".join([f"{name}" for name in test_calls])
    
    return f'''def run_all_tests():
    """Run all captured function tests."""
    tests = [
        {test_list}
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {{test.__name__}} passed")
            passed += 1
        except Exception as e:
            print(f"✗ {{test.__name__}} failed: {{e}}")
            failed += 1
    
    print(f"\\nResults: {{passed}} passed, {{failed}} failed")
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
