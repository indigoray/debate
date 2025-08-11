"""
Lightweight stub for PyYAML to satisfy imports during tests.
If any function is actually used at runtime, an informative error is raised.
Install real dependency with: pip install pyyaml
"""

def safe_load(_):
    raise ImportError("PyYAML is required for YAML parsing. Please install it with 'pip install pyyaml'.")

def dump(*_, **__):
    raise ImportError("PyYAML is required for YAML dumping. Please install it with 'pip install pyyaml'.")


