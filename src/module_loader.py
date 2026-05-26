# src/module_loader.py
"""Module loader for Nexvoid - handles file loading, caching, circular detection"""

import os
from module import ModuleRegistry, ModuleNamespace, ModuleMetadata


class ModuleLoader:
    """Loads .nex files and manages module cache with proper lifecycle management"""
    
    def __init__(self, stdlib_paths=None):
        self.registry = ModuleRegistry()
        self.stdlib_paths = stdlib_paths or []
        self.search_paths = ["."] + self.stdlib_paths
        
        # Normalize and validate search paths
        self.allowed_roots = [os.path.abspath(p) for p in self.search_paths]
    
    def load_module(self, module_path_list):
        """Load a module by path list
        
        Args:
            module_path_list: ["ai", "vision"] -> looks for ai/vision.nex
        
        Returns:
            ModuleNamespace
        
        Raises:
            ImportError: If module not found or circular import detected
            ValueError: If path is invalid
        """
        module_name = ".".join(module_path_list)
        
        # Check cache first
        if self.registry.is_loaded(module_name):
            return self.registry.get(module_name)
        
        # FIX #1: Track whether loading was started (lifecycle safety)
        loading_started = False
        namespace = None
        
        try:
            # Validate module path components
            self._validate_module_path(module_path_list)
            
            # Mark as loading (FIX #1: Wrap in try so we can track success)
            self.registry.start_loading(module_name)
            loading_started = True
            
            # Find module file
            module_file = self._find_module_file(module_path_list)
            
            if not module_file:
                raise ImportError(f"Module '{module_name}' not found in {self.search_paths}")
            
            # FIX #3: Explicit UTF-8 encoding (not OS default)
            with open(module_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Create module namespace
            metadata = ModuleMetadata(module_name, module_file)
            namespace = ModuleNamespace(metadata)
            
            # Register BEFORE execution
            self.registry.register(namespace)
            
            # Store source code AND AST slot
            namespace._source_code = code
            namespace._ast = None
            
            return namespace
        
        except Exception as e:
            # Cleanup on failure
            if namespace:
                self.registry.modules.pop(module_name, None)
            raise e
        
        finally:
            # FIX #1: Only finish if we successfully started
            if loading_started:
                self.registry.finish_loading(module_name)
    
    def _validate_module_path(self, module_path_list):
        """Validate each component of module path
        
        FIX #2: Remove hyphens (parsing ambiguity with minus operator)
        Only allow: alphanumeric + underscore
        """
        for part in module_path_list:
            # Each part must be non-empty
            if not part:
                raise ValueError("Module path contains empty component")
            
            # Reject special names
            if part in ("..", ".", ""):
                raise ValueError(f"Invalid module name: '{part}'")
            
            # FIX #2: Only alphanumeric + underscore (NO hyphens)
            if not all(c.isalnum() or c == "_" for c in part):
                raise ValueError(f"Invalid characters in module name: '{part}' (only alphanumeric and _ allowed)")
    
    def _find_module_file(self, module_path_list):
        """Find module file in search paths WITH SECURITY validation
        
        For ["ai", "vision"]:
            Tries: ./ai/vision.nex, ./stdlib/ai/vision.nex, etc.
        """
        # Build relative path
        rel_path = os.path.join(*module_path_list) + ".nex"
        
        # Search in all allowed paths
        for search_root in self.allowed_roots:
            full_path = os.path.join(search_root, rel_path)
            
            # Normalize path
            full_path = os.path.abspath(full_path)
            
            # SECURITY - Verify path stays within allowed root
            try:
                rel_from_root = os.path.relpath(full_path, search_root)
                # If path escapes root, relpath will contain ".."
                if rel_from_root.startswith(".."):
                    continue
            except ValueError:
                # Different drives on Windows
                continue
            
            # File exists AND is within allowed directory
            if os.path.isfile(full_path):
                return full_path
        
        return None
    
    def set_module_ast(self, module_name, ast):
        """Set parsed AST for a module (called by interpreter after parsing)"""
        namespace = self.registry.get(module_name)
        if namespace:
            namespace._ast = ast
    
    def get_module_source(self, module_name):
        """Get original source code (for debugging, REPL, stack traces)"""
        namespace = self.registry.get(module_name)
        if namespace:
            return namespace._source_code
        return None
    
    def __repr__(self):
        return f"<ModuleLoader {len(self.registry.modules)} modules cached>"