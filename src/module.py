# src/module.py
"""Module system architecture for Nexvoid"""


class ModuleMetadata:
    """Metadata about a module (extensible for versioning, permissions, etc.)"""
    def __init__(self, name, path, version="1.0.0"):
        self.name = name          # e.g., "math", "ai.vision"
        self.path = path          # filesystem path
        self.version = version    # versioning (future)
        self.author = None        # metadata (future)
        self.exports = set()      # exported symbols
    
    def __repr__(self):
        return f"<Module {self.name} v{self.version}>"


class ModuleNamespace:
    """Module as a namespace - contains all module symbols"""
    def __init__(self, metadata):
        self.metadata = metadata
        self.symbols = {}  # All module contents (functions, vars, submodules)
        self.loading = False  # Track circular imports
        self.loaded = False   # Fully loaded?
        self._executed = False # Has the module code been executed (for init)?
    
    def export(self, name, value):
        """Export a symbol (only exported symbols are public)"""
        self.symbols[name] = value
        self.metadata.exports.add(name)
    
    def define(self, name, value):
        """Define internal symbol (not exported)"""
        self.symbols[name] = value
    
    def get(self, name):
        """Get symbol from this module"""
        if name in self.symbols:
            return self.symbols[name]
        raise NameError(f"Module {self.metadata.name} has no symbol '{name}'")
    
    def __repr__(self):
        return f"<Namespace {self.metadata.name}>"


class ModuleRegistry:
    """Global module cache - prevent reloading, detect circular imports"""
    def __init__(self):
        self.modules = {}        # name -> ModuleNamespace
        self.loading_stack = []  # Track what's currently loading (circular detection)
    
    def register(self, module_namespace):
        """Register module in cache"""
        self.modules[module_namespace.metadata.name] = module_namespace
    
    def get(self, name):
        """Get cached module"""
        if name in self.modules:
            return self.modules[name]
        return None
    
    def is_loaded(self, name):
        """Check if module already loaded"""
        return name in self.modules
    
    def start_loading(self, name):
        """Mark module as loading (detect circular imports)"""
        if name in self.loading_stack:
            raise RuntimeError(f"Circular import detected: {' -> '.join(self.loading_stack + [name])}")
        self.loading_stack.append(name)
    
    def finish_loading(self, name):
        """Mark module as finished loading"""
        if self.loading_stack and self.loading_stack[-1] == name:
            self.loading_stack.pop()
    
    def __repr__(self):
        return f"<ModuleRegistry {len(self.modules)} modules>"


class ImportInfo:
    """Information about what's being imported"""
    def __init__(self, module_name, symbols=None, alias=None):
        self.module_name = module_name  # e.g., "math", "ai.vision"
        self.symbols = symbols or []    # ["sqrt", "sin"] or [] for all
        self.alias = alias              # e.g., {"sqrt": "root"} for aliases
    
    def __repr__(self):
        if self.symbols:
            return f"from {self.module_name} import {', '.join(self.symbols)}"
        return f"import {self.module_name}"