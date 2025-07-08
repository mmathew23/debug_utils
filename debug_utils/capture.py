"""
Function capture utilities for debugging AI training and inference.

This module provides decorators and context managers to capture function calls,
their inputs, outputs, and any errors that occur.
"""

import functools
import inspect
import traceback
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid


@dataclass
class FunctionCall:
    """Represents a captured function call with all relevant information."""
    id: str
    function_name: str
    module_name: str
    timestamp: str
    args: tuple
    kwargs: dict
    output: Any = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    function_source: Optional[str] = None
    imports: List[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


class FunctionCapture:
    """Captures function calls for later replay and testing."""
    
    def __init__(self):
        self.captured_calls: List[FunctionCall] = []
    
    def capture_decorator(self, include_source: bool = True, capture_imports: bool = True):
        """
        Decorator to capture function calls.
        
        Args:
            include_source: Whether to capture the function source code
            capture_imports: Whether to attempt to capture relevant imports
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                call_id = str(uuid.uuid4())
                
                # Get function metadata
                function_name = func.__name__
                module_name = func.__module__
                
                # Capture source code if requested
                function_source = None
                if include_source:
                    try:
                        function_source = inspect.getsource(func)
                    except (OSError, TypeError):
                        function_source = f"# Could not capture source for {function_name}"
                
                # Capture imports if requested
                imports = []
                if capture_imports:
                    imports = self._extract_imports(func)
                
                try:
                    # Execute the function
                    result = func(*args, **kwargs)
                    
                    # Create successful call record
                    call = FunctionCall(
                        id=call_id,
                        function_name=function_name,
                        module_name=module_name,
                        timestamp=datetime.now().isoformat(),
                        args=args,
                        kwargs=kwargs,
                        output=result,
                        function_source=function_source,
                        imports=imports
                    )
                    
                except Exception as e:
                    # Create failed call record
                    call = FunctionCall(
                        id=call_id,
                        function_name=function_name,
                        module_name=module_name,
                        timestamp=datetime.now().isoformat(),
                        args=args,
                        kwargs=kwargs,
                        error=traceback.format_exc(),
                        error_type=type(e).__name__,
                        function_source=function_source,
                        imports=imports
                    )
                    # Re-raise the exception
                    raise
                finally:
                    self.captured_calls.append(call)
                
                return result
            return wrapper
        return decorator
    
    def _extract_imports(self, func: Callable) -> List[str]:
        """
        Attempt to extract relevant imports for a function.
        This is a basic implementation - you might want to enhance it.
        """
        imports = []
        
        # Get the module where the function is defined
        try:
            module = inspect.getmodule(func)
            if module and hasattr(module, '__file__'):
                # Try to read the source file and extract imports
                with open(module.__file__, 'r') as f:
                    lines = f.readlines()
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        imports.append(line)
        except (OSError, TypeError, AttributeError):
            # Fallback: add common AI/ML imports
            imports = [
                "import torch",
                "import numpy as np",
                "import pandas as pd",
                "from typing import Any, Dict, List, Optional, Union"
            ]
        
        return imports
    
    def get_calls(self, function_name: Optional[str] = None) -> List[FunctionCall]:
        """Get captured calls, optionally filtered by function name."""
        if function_name:
            return [call for call in self.captured_calls if call.function_name == function_name]
        return self.captured_calls
    
    def clear_calls(self):
        """Clear all captured calls."""
        self.captured_calls.clear()
    
    def get_latest_call(self, function_name: Optional[str] = None) -> Optional[FunctionCall]:
        """Get the most recent call, optionally filtered by function name."""
        calls = self.get_calls(function_name)
        return calls[-1] if calls else None


# Global capture instance for convenience
default_capture = FunctionCapture()


def capture_function(include_source: bool = True, capture_imports: bool = True):
    """Convenience decorator using the default capture instance."""
    return default_capture.capture_decorator(include_source, capture_imports)


def get_captured_calls(function_name: Optional[str] = None) -> List[FunctionCall]:
    """Get captured calls from the default capture instance."""
    return default_capture.get_calls(function_name)


def clear_captured_calls():
    """Clear captured calls from the default capture instance."""
    default_capture.clear_calls()

