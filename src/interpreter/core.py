# src/interpreter/core.py
"""Core Nexvoid interpreter using Visitor pattern"""

from ast import arg
from platform import node

from tokens import TokenType
from ast_nodes import *
from runtime import (
    ClassInstance, ClassObject, DecoratorHandler, Environment, FunctionObject, TaskObject, BuiltinFunction,
    ReturnValue, BreakException, ContinueException,
    NexvoidRuntimeError, DEFAULT_BUILTINS, BoundMethod,
)
from module_loader import ModuleLoader
from lexer import NexvoidLexer
from parser import NexvoidParser
from module import ModuleNamespace



class NexvoidInterpreter:
    """Interprets Nexvoid AST using Visitor pattern"""
    
    def __init__(self, module_loader=None, debug=False  ):
        self.global_env = Environment()
        self.global_env.inject_builtins(DEFAULT_BUILTINS)
        self.current_env = self.global_env
        self.decorator_handler = DecoratorHandler()
        
        # Module system integration
        self.module_loader = module_loader or ModuleLoader()

        #debug mode
        self.debug = debug
        if self.debug:
            print("[DEBUG] Interpreter intialized with debug mode ON")
    
    def interpret(self, program):
        """Main entry point - execute program"""
        try:
            return self.visit(program)
        except ReturnValue:
            raise NexvoidRuntimeError("Return outside function")
        except BreakException:
            raise NexvoidRuntimeError("Break outside loop")
        except ContinueException:
            raise NexvoidRuntimeError("Continue outside loop")
    
    def visit(self, node):
        """Dispatcher - calls appropriate visit_* method"""
        method_name = f'visit_{node.__class__.__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node):
        """Default handler for unknown nodes"""
        raise NexvoidRuntimeError(f"No visit method for {node.__class__.__name__}")
    
    # Program and Block
    def visit_Program(self, node):
        """Execute all statements in program"""
        result = None
        for stmt in node.statements:
            result = self.visit(stmt)
        return result
    
    def visit_Block(self, node):
        """Execute all statements in block"""
        result = None
        for stmt in node.statements:
            result = self.visit(stmt)
        return result
    
    # Statements
    def visit_ExprStmt(self, node):
        """Execute expression statement"""
        return self.visit(node.expr)
    
    def visit_PassStmt(self, node):
        """Pass statement - do nothing"""
        return None
    
    def visit_ReturnStmt(self, node):
        """Return from function"""
        value = None
        if node.value:
            value = self.visit(node.value)
        raise ReturnValue(value)
    
    def visit_FunctionDef(self, node):
        """Store function definition and apply decorators"""
        func_obj = FunctionObject(node.name, node.params, node.body, node.return_type)
        func_obj.closure_env = self.current_env
        
        # Apply decorators if any
        if hasattr(node, 'decorators') and node.decorators:
            for decorator in node.decorators:
                if decorator.name == 'validate':
                    self.decorator_handler.apply_validate(func_obj, decorator.args)
                elif decorator.name == 'audit':
                    func_obj.audit_enabled = True
        
        self.current_env.assign(node.name, func_obj)
        return None
    
    def visit_ProtocolDef(self, node):
        """store protocol definition"""
        self.current_env.protocols[node.name] = node
        return None
    
    def visit_TaskDef(self, node):
        """Define task in current scope"""
        task_obj = TaskObject(
            name=node.name,
            params=node.params,
            body=node.body,
            closure_env=self.current_env
        )
        self.current_env.assign(node.name, task_obj)
        return None
    
    def visit_ClassDef(self, node):
        """Store class definition and apply decorators"""
        
        class_obj = ClassObject(node.name, node.fields, node.methods)
        
        # Apply decorators
        if node.decorators:
            for decorator in node.decorators:
                if decorator.name == 'secure':
                    self.decorator_handler.apply_secure(class_obj, decorator.args)
                elif decorator.name == 'validate':
                    self.decorator_handler.apply_validate(class_obj, decorator.args)
                elif decorator.name == 'audit':
                    class_obj.audit_enabled = True
        
        self.current_env.assign(node.name, class_obj)
        return None
    
    def visit_IfStmt(self, node):
        """Execute if/else statement"""
        condition = self.visit(node.condition)
        
        if self.is_truthy(condition):
            return self.visit(node.then_body)
        elif node.else_body:
            return self.visit(node.else_body)
        
        return None
    
    def visit_WhileStmt(self, node):
        """Execute while loop"""
        result = None
        while self.is_truthy(self.visit(node.condition)):
            try:
                result = self.visit(node.body)
            except BreakException:
                break
            except ContinueException:
                continue
        
        return result
    
    def visit_RepeatStmt(self, node):
        """Execute repeat loop: repeat count as var"""
        count = self.visit(node.count)
        
        # Validate count is a number
        if not isinstance(count, (int, float)):
            raise NexvoidRuntimeError(
                f"Repeat count must be number, got {type(count).__name__}"
            )
        
        # Create child scope for loop variable
        loop_env = self.current_env.create_child()
        prev_env = self.current_env
        self.current_env = loop_env
        
        result = None
        try:
            for i in range(int(count)):
                # Assign loop variable
                self.current_env.assign(node.var, i)
                
                try:
                    result = self.visit(node.body)
                except BreakException:
                    break
                except ContinueException:
                    continue
        finally:
            self.current_env = prev_env
        
        return result
    
    # Expressions
    def visit_BinaryOp(self, node):
        """Evaluate binary operation"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        op = node.op
        
        # Arithmetic
        if op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if right == 0:
                raise NexvoidRuntimeError("Division by zero")
            return left / right
        elif op == '%':
            if right == 0:
                raise NexvoidRuntimeError("Modulo by zero")
            return left % right
        elif op == '//':
            if right == 0:
                raise NexvoidRuntimeError("Floor division by zero")
            return int(left // right)
        elif op == '**':
            return left ** right
        
        # Comparison
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return left < right
        elif op == '>':
            return left > right
        elif op == '<=':
            return left <= right
        elif op == '>=':
            return left >= right
        
        # Logical
        elif op == 'and':
            return self.is_truthy(left) and self.is_truthy(right)
        elif op == 'or':
            return self.is_truthy(left) or self.is_truthy(right)
        
        else:
            raise NexvoidRuntimeError(f"Unknown operator: {op}")
    
    def visit_UnaryOp(self, node):
        """Evaluate unary operation"""
        operand = self.visit(node.operand)
        
        if node.op == '-':
            return -operand
        elif node.op == '+':
            return +operand
        elif node.op == 'not':
            return not self.is_truthy(operand)
        else:
            raise NexvoidRuntimeError(f"Unknown unary operator: {node.op}")
    
    def visit_Assignment(self, node):
        """Assign to variable"""
        value = self.visit(node.value)
        
        if isinstance(node.target, Identifier):
            self.current_env.assign(node.target.name, value)
        elif isinstance(node.target, MemberAccess):
            # Member access assignment (field or object property)
            obj = self.visit(node.target.obj)
            if isinstance(obj, ClassInstance):
                if node.target.member in obj.class_obj.encrypted_fields:
                    if not hasattr(obj, 'encrypted_values'):
                        obj.encrypted_values = set()
                    obj.encrypted_values.add(node.target.member)
                # Field assignment on class instance
                obj.fields[node.target.member] = value
            elif isinstance(obj, dict):
                # Dict-like assignment
                obj[node.target.member] = value
            else:
                raise NexvoidRuntimeError(f"Cannot assign field on {type(obj).__name__}")
        elif isinstance(node.target, IndexAccess):
            obj = self.visit(node.target.obj)
            key = self.visit(node.target.index)
            obj[key] = value
        else:
            raise NexvoidRuntimeError(f"Invalid assignment target")
        
        return value




    
    def visit_CallExpr(self, node):
        """Call function or builtin"""
        func = self.visit(node.func_expr)
        
        # Evaluate arguments
        args = [self.visit(arg) for arg in node.args]
        
        # Call builtin
        if isinstance(func, BuiltinFunction):
            return func(*args)
        
        # Call user function
        elif isinstance(func, FunctionObject):
            return self.call_function(func, args)
        
        # Call task
        elif isinstance(func, TaskObject):
            return self.call_function(func, args)
        
        elif isinstance(func, ClassObject):
            return self.instantiate_class(func, args)
        
        elif isinstance(func, BoundMethod):
            return self.call_bound_method(func.instance, func.method_name, args)
        
        else:
            raise NexvoidRuntimeError(
                f"Cannot call {type(func).__name__}"
            )
        

    def visit_MapExpr(self, node):
        """Execute map expression: map expr from var in iterable where condition"""
        iterable = self.visit(node.iterable)
        result = []
        
        for item in iterable:
            # Create new scope for loop variable
            loop_env = self.current_env.create_child()
            loop_env.assign(node.var, item)
            
            prev_env = self.current_env
            self.current_env = loop_env
            
            try:
                # Check condition if present
                if node.condition:
                    cond_result = self.visit(node.condition)
                    if not cond_result:
                        continue
                
                # Evaluate expression
                value = self.visit(node.expr)
                result.append(value)
            
            finally:
                self.current_env = prev_env
        
        return result




    
    def visit_WaitExpr(self, node):
        """Wait for task (simple sync execution for now)"""
        # For now, just execute the task call
        # TODO: Real async/await implementation
        return self.visit(node.task_call)
    
    def visit_MemberAccess(self, node):
        """Access module, instance field, or method"""
        obj = self.visit(node.obj)
        
        if isinstance(obj, ModuleNamespace):
            return obj.symbols.get(node.member)
        
        if isinstance(obj, ClassInstance):
            # Check if it's a field
            if node.member in obj.fields:
                return obj.fields[node.member]
            # Otherwise it's a method
            return BoundMethod(obj, node.member)
        
        raise NexvoidRuntimeError(f"Cannot access member on {type(obj).__name__}")

        
        # Handle dictionaries
        if isinstance(obj, dict):
            return obj.get(node.member)
        
        raise NexvoidRuntimeError(f"Cannot access member on {type(obj).__name__}")

    def visit_IndexAccess(self, node):
        """Access array/map element: arr[0], m["key"]"""
        obj = self.visit(node.obj)
        index = self.visit(node.index)

        if isinstance(obj, list):
            try:
                return obj[int(index)]
            except (IndexError, ValueError):
                raise NexvoidRuntimeError(f"Array index out of range: {index}")
        elif isinstance(obj, dict):
            if index not in obj:
                raise NexvoidRuntimeError(f"Map key not found: {index}")
            return obj[index]
        else:
            raise NexvoidRuntimeError(f"Cannot index into {type(obj).__name__}")


    
    # Literals
    def visit_NumberLiteral(self, node):
        """Return number literal"""
        try:
            if '.' in str(node.value):
                return float(node.value)
            return int(node.value)
        except ValueError:
            raise NexvoidRuntimeError(f"Invalid number: {node.value}")
    
    def visit_StringLiteral(self, node):
        """Return string literal"""
        return node.value
    


    def visit_StringLiteral(self, node):
        """Return string literal"""
        return node.value

    def visit_StringInterpolation(self, node):
        """Evaluate string interpolation with structured parts"""
        result = ""
        for part in node.parts:
            if part.kind == "text":
                result += part.value
            elif part.kind == "expr":
                value = self.visit(part.value)
                result += str(value)
        return result

    def visit_BoolLiteral(self, node):
        """Return boolean literal"""
        return node.value
    
    
    


    


    
    

    

    






    def visit_ArrayLiteral(self, node):
        """Evaluate array literal: array(1, 2, 3)"""
        elements = []
        for element in node.elements:
            elements.append(self.visit(element))
        return elements
    
    def visit_MapLiteral(self, node):
        """Evaluate map literal: map(name = "value", level = 99)"""
        map_dict = {}
        for key, value_expr in node.pairs:
            value = self.visit(value_expr)
            map_dict[str(key)] = value
        return map_dict

    
   



    





    def visit_BoolLiteral(self, node):
        """Return boolean literal"""
        return node.value
    
    def visit_Identifier(self, node):
        """Look up identifier with debug info and @field support"""
        if self.debug:
            print(f"[DEBUG] Looking up identifier: {node.name}")
        
        # Handle field access: @fieldname
        if node.name.startswith("@"):
            field_name = node.name[1:] # Remove @ prefix
            
            try:
                instance = self.current_env.get("@instance")
                if not isinstance(instance, ClassInstance):
                    raise NexvoidRuntimeError(f"Field access outside of class context")
                
                if self.debug:
                    print(f"[DEBUG] Accessing field: {field_name}")
                
                return instance.get_field(field_name)
            except NexvoidRuntimeError as e:
                if self.debug:
                    print(f"[DEBUG] Field access failed: {field_name}")
                raise
        
        # Regular identifier lookup
        try:
            return self.current_env.get(node.name)
        except NexvoidRuntimeError as e:
            if self.debug:
                print(f"[DEBUG] Identifier not found: {node.name}")
            raise




    
    # Helper methods
    def is_truthy(self, value):
        """Determine if value is truthy"""
        if value is None or value is False:
            return False
        if value == 0 or value == "" or value == []:
            return False
        return True
    
    def call_function(self, func_obj, args):
        """Call a user-defined function"""
        if func_obj.name in self.decorator_handler.validators:
            validators = self.decorator_handler.validators[func_obj.name]
            if 'min_length' in validators:
                min_len = validators['min_length']
                if args and isinstance(args[0], str):
                    if len(args[0])<min_len:
                        raise NexvoidRuntimeError(
                            f"validation failed: {func_obj.name} requires min_length={min_len}"
                        )
        # Validate argument count
        if len(args) != len(func_obj.params):
            raise NexvoidRuntimeError(
                f"{func_obj.name}() expects {len(func_obj.params)} "
                f"arguments, got {len(args)}"
            )
        
        # Create new environment for function execution
        func_env = func_obj.closure_env.create_child()
        
        # Bind parameters
        for param, arg in zip(func_obj.params, args):
    # Handle both old format (string) and new format (tuple)
            if isinstance(param, tuple):
                param_name = param[0]
            else:
                param_name = param
            func_env.assign(param_name, arg)
        
        # Execute function body
        prev_env = self.current_env
        self.current_env = func_env
        
        result = None
        try:
            result = self.visit(func_obj.body)
        except ReturnValue as ret:
            result = ret.value
        finally:
            self.current_env = prev_env

        if func_obj.audit_enabled:
            self.decorator_handler.apply_audit(func_obj.name, args,  result)
        
        return result
    
    def instantiate_class(self, class_obj, args):
        """Create an instance of a class"""
        instance = ClassInstance(class_obj)
        
        # Find and call "create" method (constructor)
        create_method = None
        for method in class_obj.methods:
            if method.name == "create":
                create_method = method
                break
        
        if create_method:
            # Create environment for constructor
            init_env = self.current_env.create_child()
            
            # Bind parameters
            if len(args) != len(create_method.params):
                raise NexvoidRuntimeError(
                    f"{class_obj.name}.create() expects {len(create_method.params)} "
                    f"arguments, got {len(args)}"
                )
            
            for param, arg in zip(create_method.params, args):
                init_env.assign(param, arg)
            
            # Store instance reference as "this"
            init_env.assign("this", instance)
            
            # Execute constructor
            prev_env = self.current_env
            self.current_env = init_env
            
            try:
                self.visit(create_method.body)
            except ReturnValue:
                pass
            finally:
                self.current_env = prev_env
        
        return instance








    

    
    def call_bound_method(self, instance, method_name, args):
        """call a method on an instance"""
        method = None
        for m in instance.class_obj.methods:
            if m.name == method_name:
                method = m
                break

        if not method:
            raise NexvoidRuntimeError(f"Method '{method_name}' not found")
        
        # Create environment for method with instance context
        method_env = self.current_env.create_child()

        #bind parameters
        for param, arg in zip(method.params, args):
            method_env.assign(param, arg)

            #bind instance
        method_env.assign("this", instance)
        #execute method
        prev_env = self.current_env
        self.current_env = method_env

        result = None
        try:
            self.visit(method.body)
        except ReturnValue as ret:
            result = ret.value
        
        finally:
            self.current_env = prev_env
        return result




    
    # Module system methods
    def visit_ImportStmt(self, node):
        """Handle: import module_name [as alias]
        
        Examples:
            import math
            import ai.vision as vision
        """
        module_name = ".".join(node.module_path)
        
        try:
            # Load module file
            namespace = self.module_loader.load_module(node.module_path)
            
            # Execute module code if not already executed
            self._execute_module(namespace)
            
            # Use alias if provided, otherwise use last part of path
            alias = node.alias or node.module_path[-1]
            
            # Add module namespace to current environment
            self.current_env.assign(alias, namespace)
            
            return None
        
        except ImportError as e:
            raise NexvoidRuntimeError(f"Import error: {e}")





    def visit_FromImportStmt(self, node):
            """Handle: from module_name import symbol1, symbol2 [as alias]
            
            Examples:
                from math import sqrt, sin
                from ai.vision import detect as detect_objects
                from string import *
            """
            module_name = ".".join(node.module_path)
            
            try:
                # Load module file
                namespace = self.module_loader.load_module(node.module_path)
                
                # Execute module code if not already executed
                self._execute_module(namespace)
                
                # Import symbols from module
                if "*" in node.symbols:
                    # from module import *
                    for name, value in namespace.symbols.items():
                        if not name.startswith("_"): # Skip private symbols
                            self.current_env.assign(name, value)
                else:
                    # from module import specific symbols
                    for symbol in node.symbols:
                        if symbol not in namespace.symbols:
                            raise ImportError(f"Module '{module_name}' has no symbol '{symbol}'")
                        
                        value = namespace.symbols[symbol]
                        
                        # Check for alias: "from math import sqrt as root"
                        alias = node.aliases.get(symbol, symbol)
                        self.current_env.assign(alias, value)
                
                return None
            
            except ImportError as e:
                raise NexvoidRuntimeError(f"Import error: {e}")

    def _execute_module(self, namespace):
        """Execute a module's code in its namespace"""
        # Skip if already executed
        if namespace._executed:
            return
        
        # Get source code from module
        source_code = self.module_loader.get_module_source(namespace.metadata.name)
        
        if not source_code:
            raise NexvoidRuntimeError(f"Module has no source code: {namespace.metadata.name}")
        
        # Parse module code
        try:
            lexer = NexvoidLexer(source_code)
            tokens = lexer.tokenize()
            parser = NexvoidParser(tokens)
            module_ast = parser.parse()
        except SyntaxError as e:
            raise NexvoidRuntimeError(f"Syntax error in module {namespace.metadata.name}: {e}")
        
        # Execute in module's namespace
        prev_env = self.current_env
        module_env = self.global_env.create_child()
        self.current_env = module_env
        
        try:
            # Execute all statements in module
            for stmt in module_ast.statements:
                self.visit(stmt)
                
                # If it's a function or task, export it to namespace
                if isinstance(stmt, (FunctionDef, TaskDef)):
                    symbol_name = stmt.name
                    value = module_env.get(symbol_name)
                    namespace.symbols[symbol_name] = value
            
            # Store all module-level variables in namespace
            for name, value in module_env.values.items():
                if not name.startswith("_"): # Skip private (_name)
                    namespace.symbols[name] = value
        
        finally:
            self.current_env = prev_env
        
        # Mark as executed
        namespace._executed = True