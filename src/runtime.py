# src/runtime.py
"""Runtime environment for Nexvoid interpreter"""


class FunctionObject:
    def __init__(self, name, params, body, return_type=None):
        self.name = name
        self.params = params # List of (param_name, param_type) tuples
        self.body = body
        self.return_type = return_type
        self.audit_enabled = False
    
    def __call__(self, *args, **kwargs):
        """Functions are callable objects"""
        raise NotImplementedError("Call handled by interpreter")
    
    def __repr__(self):
        return f"<Function {self.name}>"


class TaskObject:
    """Represents a task (async function) as a first-class callable value"""
    def __init__(self, name, params, body, closure_env):
        self.name = name
        self.params = params
        self.body = body
        self.closure_env = closure_env
        self.is_task = True
    
    def __call__(self, *args, **kwargs):
        """Tasks are callable objects"""
        raise NotImplementedError("Call handled by interpreter")
    
    def __repr__(self):
        return f"<Task {self.name}>"
    

class ClassObject:
    """Represents a class definition"""
    def __init__(self, name, fields, methods):
        self.name = name # "User"
        self.fields = fields # List of FieldDecl nodes
        self.methods = methods # List of FunctionDef nodes
        self.decorators = None # Can be set later
    
    def __repr__(self):
        return f"ClassObject({self.name})"
    
class ClassObject:
    """Represents a class definition"""
    def __init__(self, name, fields, methods):
        self.name = name
        self.fields = fields
        self.methods = methods
        self.decorators = None
        self.audit_enabled = False
        self.encrypted_fields = set()


class ClassInstance:
    """Represents an instance of a class"""
    def __init__(self, class_obj):
        self.class_obj = class_obj # Reference to ClassObject
        self.fields = {} # {"username": "Alice", "email": "alice@example.com"}
    
    def get_field(self, field_name):
        """Get field value"""
        if field_name not in self.fields:
            raise NexvoidRuntimeError(f"Field '{field_name}' not found in {self.class_obj.name}")
        return self.fields[field_name]
    
    def set_field(self, field_name, value):
        """Set field value"""
        self.fields[field_name] = value
    
    def __repr__(self):
        return f"Instance({self.class_obj.name})"


class BoundMethod:
    """A method bound to an instance"""
    def __init__(self, instance, method_name):
        self.instance = instance
        self.method_name = method_name

    def __repr__(self):
        return f"BoundMethod({self.instance.class_obj.name}.{self.method_name})"
        






class BuiltinFunction:
    """Wrapper for built-in functions - also callable"""
    def __init__(self, name, func, arity=None):
        self.name = name
        self.func = func
        self.arity = arity # Expected number of args (None = variable)
    
    def __call__(self, *args):
        """Built-in functions are directly callable"""
        if self.arity is not None and len(args) != self.arity:
            raise NexvoidRuntimeError(
                f"{self.name}() expects {self.arity} arguments, got {len(args)}"
            )
        return self.func(*args)
    
    def __repr__(self):
        return f"<Builtin {self.name}>"


class Environment:
    """Unified namespace for variables, functions, and builtins"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {} # FIX #1: Everything here is callable-compatible
        self.protocols = {} # Protocol definitions (name -> ProtocolDef node)
    
    def assign(self, name, value):
        """Assign to variable (Python-style: create in local scope if not exists)"""
        # FIX #2: Simpler semantics - always assigns to current scope
        self.values[name] = value
    
    def get(self, name):
        """Look variable with hhelpful error messages"""
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        # get all variable variables for suggestions
        available = list(self.values.keys())
        if self.parent:
            available.extend(self.parent.get_all_vars())
        context = ErrorContext(
            f"Undefined variable '{name}'",
            available_vars=available
        )
        raise NexvoidRuntimeError(context.format_error())
    
    def get_all_vars(self):
        """Get all varables in scope chain"""
        vars_list = list(self.values.keys())
        if self.parent:
            vars_list.extend(self.parent.get_all_vars())
        return vars_list


    def exists(self, name):
        """Check if variable/function exists"""
        if name in self.values:
            return True
        
        if self.parent:
            return self.parent.exists(name)
        
        return False
    
    def inject_builtin(self, name, builtin_func):
        """Inject built-in function into global scope"""
        # FIX #3: Builtins are callable objects stored same as everything
        self.values[name] = builtin_func
    
    def inject_builtins(self, builtins_dict):
        """Inject multiple built-ins at once"""
        for name, func in builtins_dict.items():
            self.inject_builtin(name, func)
    
    def create_child(self):
        """Create child scope (for function calls, blocks)"""
        return Environment(parent=self)


class ReturnValue(Exception):
    """Exception to signal return from function"""
    def __init__(self, value):
        self.value = value
        super().__init__()


class BreakException(Exception):
    """Exception to signal break from loop"""
    pass


class ContinueException(Exception):
    """Exception to signal continue in loop"""
    pass


class NexvoidRuntimeError(Exception):
    """General runtime error"""
    pass



class ErrorContext:
    """Enhanced error reporting with suggestions"""
    def __init__(self, message, line=None, col=None, available_vars=None, available_funcs=None):
        self.message = message
        self.line = line
        self.col = col
        self.available_vars = available_vars or []
        self.available_funcs = available_funcs or []
    
    def suggest_similar(self, name, items):
        """Find similar names (typo suggestions)"""
        import difflib
        matches = difflib.get_close_matches(name, items, n=3, cutoff=0.6)
        return matches
    
    def format_error(self):
        """Format error with context and suggestions"""
        error_str = f"❌ {self.message}"
        
        if self.line and self.col:
            error_str += f" at line {self.line}, col {self.col}"
        
        # Add suggestions if we have undefined variable
        if "Undefined" in self.message and self.available_vars:
            # Extract variable name from message
            parts = self.message.split("'")
            if len(parts) >= 2:
                var_name = parts[1]
                suggestions = self.suggest_similar(var_name, self.available_vars)
                if suggestions:
                    error_str += f"\n 💡 Did you mean: {', '.join(suggestions)}?"
            error_str += f"\n 📋 Available variables: {', '.join(self.available_vars[:5])}"
        
        return error_str
    
class DecoratorHandler:
    """Handles decorator enforcement: @secure, @validate, @encrypt, @audit"""
    
    def __init__(self):
        self.validators = {}
        self.encrypted_fields = set()
        self.audit_log = []
    
    def apply_secure(self, class_obj, decorator_args):
        """Apply @secure(encrypt=field, audit=true)"""
        if 'encrypt' in decorator_args:
            field = decorator_args['encrypt']
            self.encrypted_fields.add(field)
    
    def apply_validate(self, func_obj, decorator_args):
        """Apply @validate(min_length=8, etc)"""
        self.validators[func_obj.name] = decorator_args
    
    def apply_audit(self, func_name, args, result):
        """Log function calls for auditing"""
        log_entry = {
            'function': func_name,
            'args': args,
            'result': result,
            'timestamp': str(__import__('datetime').datetime.now())
        }
        self.audit_log.append(log_entry)
    
    def get_audit_log(self):
        """Return audit log"""
        return self.audit_log




    

    










# Built-in cout implementation
def builtin_cout(*args):
    """FIX #3: Built-in cout function that actually works"""
    output = " ".join(str(arg) for arg in args)
    print(output)
    return None

# Built-in input implementation
def builtin_input(prompt=""):
    """Built-in input function - reads user input, returns  string"""
    if prompt:
        return input(str(prompt))
    return input()

# Built-in len implementation
def builtin_len(obj):
    """FIX #3: Built-in len function"""
    if isinstance(obj, str):
        return len(obj)
    if isinstance(obj, list):
        return len(obj)
    raise NexvoidRuntimeError(f"len() not supported for {type(obj).__name__}")


# Built-in type implementation
def builtin_type(obj):
    """FIX #3: Built-in type function"""
    if isinstance(obj, bool):
        return "bool"
    if isinstance(obj, int) or isinstance(obj, float):
        return "number"
    if isinstance(obj, str):
        return "string"
    if isinstance(obj, FunctionObject):
        return "function"
    if isinstance(obj, TaskObject):
        return "task"
    return type(obj).__name__




#built-in int implementation
def builtin_int(obj):
    """built-in int function - converts to integer"""
    if isinstance(obj, bool):
        return 1 if obj else 0
    if isinstance(obj, (int, bool)):
        return int(obj)
    if isinstance(obj, str):
        try:
            return int(obj)
        except ValueError:
            raise NexvoidRuntimeError(f"Cannot convert '{obj}' to int")
    return int(obj)


#built-in float implementation
def builtin_float(obj):
    """built-in float function - converts to float"""
    if isinstance(obj, str):
        try:
            return float(obj)
        except ValueError:
            raise NexvoidRuntimeError(f"Cannot convert '{obj}' to float")
    return float(obj)

    
        
# Built-in str implementation
def builtin_str(obj):
    """built-in str function - converts to string"""
    return str(obj)


# Built-in min implementation
def builtin_min(*args):
    """Built-in min function - find minimum value"""
    if len(args) == 0:
        raise NexvoidRuntimeError("min() expects at least 1 argument")
    if len(args) == 1:
        
        obj = args[0]
        if isinstance(obj, (list, tuple, str)):
            return min(obj)
        else:
            return obj
    
    return min(args)



    # Built-in max implementation
def builtin_max(*args):
    """Built-in max function - find maximum value"""
    if len(args) == 0:
        raise NexvoidRuntimeError("max() expects at least 1 argument")
    if len(args) == 1:
        
        obj = args[0]
        if isinstance(obj, (list, tuple, str)):
            return max(obj)
        else:
            return obj
    
    return max(args)


# Built-in pow implementation
def builtin_pow(base, exponent):
    """Built-in pow function - raise base to exponent power"""
    if not isinstance(base, (int, float)):
        raise NexvoidRuntimeError(f"pow() base must be number, got {type(base).__name__}")
    if not isinstance(exponent, (int, float)):
        raise NexvoidRuntimeError(f"pow() exponent must be number, got {type(exponent).__name__}")
    return pow(base, exponent)



# Built-in sqrt implementation
def builtin_sqrt(num):
    """Built-in sqrt function - square root"""
    if not isinstance(num, (int, float)):
        raise NexvoidRuntimeError(f"sqrt() expects number, got {type(num).__name__}")
    if num < 0:
        raise NexvoidRuntimeError(f"sqrt() cannot take square root of negative number")
    return num ** 0.5



# Built-in round implementation
def builtin_round(num, decimals=0):
    """Built-in round function - round to n decimal places"""
    if not isinstance(num, (int, float)):
        raise NexvoidRuntimeError(f"round() expects number, got {type(num).__name__}")
    if not isinstance(decimals, int):
        raise NexvoidRuntimeError(f"round() decimals must be integer, got {type(decimals).__name__}")
    return round(num, int(decimals))



# Built-in floor implementation
def builtin_floor(num):
    """Built-in floor function - round down to nearest integer"""
    if not isinstance(num, (int, float)):
        raise NexvoidRuntimeError(f"floor() expects number, got {type(num).__name__}")
    import math
    return math.floor(num)


    # Built-in ceil implementation
def builtin_ceil(num):
    """Built-in ceil function - round up to nearest integer"""
    if not isinstance(num, (int, float)):
        raise NexvoidRuntimeError(f"ceil() expects number, got {type(num).__name__}")
    import math
    return math.ceil(num)

# Built-in upper implementation
def builtin_upper(s):
    """Built-in upper function - convert string to uppercase"""
    if not isinstance(s, str):
        raise NexvoidRuntimeError(f"upper() expects string, got {type(s).__name__}")
    return s.upper()

    # Built-in lower implementation
def builtin_lower(s):
    """Built-in lower function - convert string to lowercase"""
    if not isinstance(s, str):
        raise NexvoidRuntimeError(f"lower() expects string, got {type(s).__name__}")
    return s.lower()



# Default builtins to inject
DEFAULT_BUILTINS = {
    'cout': BuiltinFunction('cout', builtin_cout, arity=None),
    #alliases for cout
    'print': BuiltinFunction('print', builtin_cout, arity=None),
    'say': BuiltinFunction('say', builtin_cout, arity=None),
    'broadcast': BuiltinFunction('broadcast', builtin_cout, arity=None),
    'flex': BuiltinFunction('flex', builtin_cout, arity=None),
    'yasama': BuiltinFunction('yasama', builtin_cout, arity=None),
    'ebinyo': BuiltinFunction('ebinyo', builtin_cout, arity=None),


    'input': BuiltinFunction('input', builtin_input, arity=None),
    # Alias for input
    'scan': BuiltinFunction('scan', builtin_input, arity=None), 
    'read': BuiltinFunction('read', builtin_input, arity=None),
    'ask': BuiltinFunction('ask', builtin_input, arity=None),
    'capture': BuiltinFunction('capture', builtin_input, arity=None),
    'loot': BuiltinFunction('loot', builtin_input, arity=None),
    'grab': BuiltinFunction('grab', builtin_input, arity=None),
    'listen': BuiltinFunction('listen', builtin_input, arity=None),
    'beg': BuiltinFunction('beg', builtin_input, arity=None),
    'yoo': BuiltinFunction('yoo', builtin_input, arity=None),
    'confess': BuiltinFunction('confess', builtin_input, arity=None),

    'len': BuiltinFunction('len', builtin_len, arity=1),
    #alliases for len
    'length': BuiltinFunction('length', builtin_len, arity=1),
    'size': BuiltinFunction('size', builtin_len, arity=1),
    'count': BuiltinFunction('count', builtin_len, arity=1),
    'howmany': BuiltinFunction('howmany', builtin_len, arity=1),
    'how_many': BuiltinFunction('how_many', builtin_len, arity=1),

    'type': BuiltinFunction('type', builtin_type, arity=1),
    'str': BuiltinFunction('str', builtin_str, arity=1),
    'int': BuiltinFunction('int', builtin_int, arity=1),
    'float': BuiltinFunction('float', builtin_float, arity=1),
    'min': BuiltinFunction('min', builtin_min, arity=None),
    'max': BuiltinFunction('max', builtin_max, arity=None),
    'pow': BuiltinFunction('pow', builtin_pow, arity=2),
    'sqrt': BuiltinFunction('sqrt', builtin_sqrt, arity=1),
    'round': BuiltinFunction('round', builtin_round, arity=None),
    'floor': BuiltinFunction('floor', builtin_floor, arity=1),
    'ceil': BuiltinFunction('ceil', builtin_ceil, arity=1),
    'upper': BuiltinFunction('upper', builtin_upper, arity=1),
    'lower': BuiltinFunction('lower', builtin_lower, arity=1),
}
