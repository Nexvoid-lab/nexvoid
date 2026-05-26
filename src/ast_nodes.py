"""AST Node definitions for Nexvoid parser"""


class ASTNode:
    """Base class for all AST nodes"""
    def __init__(self, line=None, col=None):
        self.line = line
        self.col = col


# Program (root)
class Program(ASTNode):
    def __init__(self, statements, line=None, col=None):
        super().__init__(line, col)
        self.statements = statements
    
    def __repr__(self):
        return f"Program({len(self.statements)} statements)"


# Block node
class Block(ASTNode):
    def __init__(self, statements, line=None, col=None):
        super().__init__(line, col)
        self.statements = statements
    
    def __repr__(self):
        return f"Block({len(self.statements)} statements)"


# Statements
class FunctionDef(ASTNode):
    def __init__(self, name, params, body, return_type=None, line=None, col=None):
        self.name = name
        self.params = params
        self.body = body
        self.return_type = return_type # Type annotation
        self.line = line
        self.col = col


    
    def __repr__(self):
        return f"FunctionDef({self.name}, params={self.params})"


class TaskDef(ASTNode):
    def __init__(self, name, params, body, line=None, col=None):
        super().__init__(line, col)
        self.name = name
        self.params = params
        self.body = body
    
    def __repr__(self):
        return f"TaskDef({self.name}, params={self.params})"




class FieldDecl(ASTNode):
    def __init__(self, name, field_type, visibility, line=None, col=None):
        super().__init__(line, col)
        self.name = name
        self.field_type = field_type
        self.visibility = visibility
    
    def __repr__(self):
        return f"FieldDecl({self.visibility} {self.name}: {self.field_type})"


class Decorator(ASTNode):
    def __init__(self, name, args, line=None, col=None):
        super().__init__(line, col)
        self.name = name
        self.args = args
    
    def __repr__(self):
        return f"Decorator(@{self.name})"


class ClassDef(ASTNode):
    def __init__(self, name, decorators, fields, methods, line=None, implements=None, col=None):
        super().__init__(line, col)
        self.name = name
        self.decorators = decorators
        self.fields = fields
        self.methods = methods
        self.implements = implements
        self.line = line
        self.col = col
    def __repr__(self):
        return f"ClassDef({self.name}, {len(self.fields)} fields, {len(self.methods)} methods)"






class IfStmt(ASTNode):
    def __init__(self, condition, then_body, else_body=None, line=None, col=None):
        super().__init__(line, col)
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body
    
    def __repr__(self):
        return f"IfStmt(condition=...)"


class WhileStmt(ASTNode):
    def __init__(self, condition, body, line=None, col=None):
        super().__init__(line, col)
        self.condition = condition
        self.body = body
    
    def __repr__(self):
        return f"WhileStmt(condition=...)"


class RepeatStmt(ASTNode):
    def __init__(self, count, var, body, line=None, col=None):
        super().__init__(line, col)
        self.count = count
        self.var = var
        self.body = body
    
    def __repr__(self):
        return f"RepeatStmt(repeat {self.count} as {self.var})"


class ReturnStmt(ASTNode):
    def __init__(self, value, line=None, col=None):
        super().__init__(line, col)
        self.value = value
    
    def __repr__(self):
        return f"ReturnStmt(value=...)"


class PassStmt(ASTNode):
    def __init__(self, line=None, col=None):
        super().__init__(line, col)
    
    def __repr__(self):
        return f"PassStmt()"


class ExprStmt(ASTNode):
    def __init__(self, expr, line=None, col=None):
        super().__init__(line, col)
        self.expr = expr
    
    def __repr__(self):
        return f"ExprStmt(expr=...)"


# Expressions
class BinaryOp(ASTNode):
    def __init__(self, left, op, right, line=None, col=None):
        super().__init__(line, col)
        self.left = left
        self.op = op
        self.right = right
    
    def __repr__(self):
        return f"BinaryOp({self.op})"


class UnaryOp(ASTNode):
    def __init__(self, op, operand, line=None, col=None):
        super().__init__(line, col)
        self.op = op
        self.operand = operand
    
    def __repr__(self):
        return f"UnaryOp({self.op})"


class CallExpr(ASTNode):
    def __init__(self, func_expr, args, line=None, col=None):
        super().__init__(line, col)
        self.func_expr = func_expr
        self.args = args
    
    def __repr__(self):
        return f"CallExpr(func=..., {len(self.args)} args)"


class WaitExpr(ASTNode):
    def __init__(self, task_call, line=None, col=None):
        super().__init__(line, col)
        self.task_call = task_call
    
    def __repr__(self):
        return f"WaitExpr(task=...)"


class MemberAccess(ASTNode):
    def __init__(self, obj, member, line=None, col=None):
        super().__init__(line, col)
        self.obj = obj
        self.member = member
    
    def __repr__(self):
        return f"MemberAccess({self.obj}.{self.member})"


class IndexAccess(ASTNode):
    def __init__(self, obj, index, line=None, col=None):
        super().__init__(line, col)
        self.obj = obj
        self.index = index
    
    def __repr__(self):
        return f"IndexAccess({self.obj}[...])"


class Assignment(ASTNode):
    def __init__(self, target, value, line=None, col=None):
        super().__init__(line, col)
        self.target = target
        self.value = value
    
    def __repr__(self):
        return f"Assignment({self.target} = ...)"


# Literals
class NumberLiteral(ASTNode):
    def __init__(self, value, line=None, col=None):
        super().__init__(line, col)
        self.value = value
    
    def __repr__(self):
        return f"NumberLiteral({self.value})"


class StringLiteral(ASTNode):
    def __init__(self, value, line=None, col=None):
        super().__init__(line, col)
        self.value = value
    
    def __repr__(self):
        return f"StringLiteral({self.value!r})"


class BoolLiteral(ASTNode):
    def __init__(self, value, line=None, col=None):
        super().__init__(line, col)
        self.value = value
    
    def __repr__(self):
        return f"BoolLiteral({self.value})"


class ArrayLiteral(ASTNode):
    def __init__(self, elements, line=None, col=None):
        super().__init__(line, col)
        self.elements = elements # List of expressions
    
    def __repr__(self):
        return f"ArrayLiteral({len(self.elements)} elements)"


class MapLiteral(ASTNode):
    def __init__(self, pairs, line=None, col=None):
        super().__init__(line, col)
        self.pairs = pairs # List of (key, value) tuples
    
    def __repr__(self):
        return f"MapLiteral({len(self.pairs)} pairs)"


class StringPart(ASTNode):
    def __init__(self, kind, value, line=None, col=None):
        super().__init__(line, col)
        self.kind = kind # "text" or "expr"
        self.value = value # str if text, ASTNode if expr
    
    def __repr__(self):
        return f"StringPart({self.kind})"


class StringInterpolation(ASTNode):
    def __init__(self, parts, line=None, col=None):
        super().__init__(line, col)
        self.parts = parts # List of StringPart nodes
    
    def __repr__(self):
        return f"StringInterpolation({len(self.parts)} parts)"


class Identifier(ASTNode):
    def __init__(self, name, line=None, col=None):
        super().__init__(line, col)
        self.name = name
    
    def __repr__(self):
        return f"Identifier({self.name})"


# Import statements
class ImportStmt(ASTNode):
    def __init__(self, module_path, alias=None, line=None, col=None):
        super().__init__(line, col)
        self.module_path = module_path # LIST: ["ai", "vision"]
        self.alias = alias # "tf" for "import tensorflow as tf"
    
    def __repr__(self):
        path_str = ".".join(self.module_path)
        if self.alias:
            return f"ImportStmt({path_str} as {self.alias})"
        return f"ImportStmt({path_str})"


class FromImportStmt(ASTNode):
    def __init__(self, module_path, symbols, aliases=None, line=None, col=None):
        super().__init__(line, col)
        self.module_path = module_path # LIST: ["math"]
        self.symbols = symbols # ["sqrt", "sin"] or ["*"]
        self.aliases = aliases or {} # {"sqrt": "root"} for renaming
    
    def __repr__(self):
        path_str = ".".join(self.module_path)
        symbols_str = ", ".join(self.symbols)
        return f"FromImportStmt(from {path_str} import {symbols_str})"


class ExportStmt(ASTNode):
    def __init__(self, name, line=None, col=None):
        super().__init__(line, col)
        self.name = name # Symbol name to export
    
    def __repr__(self):
        return f"ExportStmt(export {self.name})"
    
class MapExpr(ASTNode):
    """map expr from var in iterable [where condition]"""
    def __init__(self, expr, var, iterable, condition=None, line=None, col=None):
        self.expr = expr
        self.var = var
        self.iterable = iterable
        self.condition = condition
        self.line = line
        self.col = col

class ProtocolMethod(ASTNode):
    """Method signature in a protocol"""
    def __init__(self, name, params, return_type=None, line=None, col=None):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.line = line
        self.col = col


class ProtocolDef(ASTNode):
    """protocol Name INDENT methods DEDENT"""
    def __init__(self, name, methods, line=None, col=None):
        self.name = name
        self.methods = methods
        self.line = line
        self.col = col

class TypeAnnotation(ASTNode):
    """Type annotation like: int, text, bool, float, void"""
    def __init__(self, type_name, line=None, col=None):
        self.type_name = type_name
        self.line = line
        self.col = col


class Parameter(ASTNode):
    """Function parameter with optional type"""
    def __init__(self, name, param_type=None, line=None, col=None):
        self.name = name
        self.param_type = param_type
        self.line = line
        self.col = col