"""Parser for Nexvoid - converts tokens to AST"""

from tokens import TokenType
from ast_nodes import *
from runtime import NexvoidRuntimeError
from lexer import NexvoidLexer


class NexvoidParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def error(self, msg):
        token = self.current_token()
        raise SyntaxError(f"Parser Error at L{token.line}:C{token.col} - {msg}")

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def peek_token(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1

    def expect(self, token_type):
        token = self.current_token()
        if token.type != token_type:
            self.error(f"Expected {token_type}, got {token.type}")
        self.advance()
        return token

    def match(self, *token_types):
        return self.current_token().type in token_types

    def consume(self, token_type):
        if self.match(token_type):
            token = self.current_token()
            self.advance()
            return token
        return None

    def skip_newlines(self):
        while self.consume(TokenType.NEWLINE):
            pass

    def synchronize(self):
        self.advance()
        while not self.match(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                self.advance()
                return
            if self.match(
                TokenType.FUN,
                TokenType.CLASS,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.REPEAT,
                TokenType.RETURN,
                TokenType.IMPORT,
                TokenType.FROM,
                TokenType.TASK,
            ):
                return
            self.advance()

    def parse(self):
        statements = []
        while not self.match(TokenType.EOF):
            self.skip_newlines()
            if self.match(TokenType.EOF):
                break
            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            except SyntaxError as e:
                print(e)
                self.synchronize()
            self.skip_newlines()

        if statements:
            line = statements[0].line
            col = statements[0].col
        else:
            line = 1
            col = 1

        return Program(statements, line, col)

    def parse_statement(self):
        self.skip_newlines()

        decorators=[]
        while self.match(TokenType.AT):
            decorators.append(self.parse_decorator())
            self.skip_newlines()


        if self.match(TokenType.IMPORT):
            return self.parse_import_stmt()

        if self.match(TokenType.FROM):
            return self.parse_from_import_stmt()

        if self.match(TokenType.CLASS):
            return self.parse_class_def()

        if self.match(TokenType.FUN):
            return self.parse_function_def()

        if self.match(TokenType.TASK):
            return self.parse_task_def()

        if self.match(TokenType.IF):
            return self.parse_if_stmt()

        if self.match(TokenType.WHILE):
            return self.parse_while_stmt()

        if self.match(TokenType.REPEAT):
            return self.parse_repeat_stmt()

        if self.match(TokenType.RETURN):
            return self.parse_return_stmt()

        if self.match(TokenType.PROTOCOL):
            return self.parse_protocol_def()

        if self.match(TokenType.PASS):
            token = self.current_token()
            self.advance()
            return PassStmt(line=token.line, col=token.col)

        return self.parse_expr_stmt()

    def parse_import_stmt(self):
        import_token = self.expect(TokenType.IMPORT)
        module_path = self.parse_module_path()
        alias = None

        if self.match(TokenType.AS):
            self.advance()
            alias_token = self.expect(TokenType.IDENT)
            alias = alias_token.value

        return ImportStmt(
            module_path,
            alias,
            import_token.line,
            import_token.col
        )

    def parse_from_import_stmt(self):
        from_token = self.expect(TokenType.FROM)
        module_path = self.parse_module_path()
        self.expect(TokenType.IMPORT)

        symbols = []
        aliases = {}

        if self.match(TokenType.MULT):
            self.advance()
            symbols = ["*"]
        else:
            while True:
                symbol_token = self.expect(TokenType.IDENT)
                symbol_name = symbol_token.value
                symbols.append(symbol_name)

                if self.match(TokenType.AS):
                    self.advance()
                    alias_token = self.expect(TokenType.IDENT)
                    aliases[symbol_name] = alias_token.value

                if not self.match(TokenType.COMMA):
                    break

                self.advance()

        return FromImportStmt(
            module_path,
            symbols,
            aliases,
            from_token.line,
            from_token.col
        )

    def parse_module_path(self):
        parts = []
        first = self.expect(TokenType.IDENT)
        parts.append(first.value)

        while self.match(TokenType.DOT):
            self.advance()
            part = self.expect(TokenType.IDENT)
            parts.append(part.value)

        return parts

    def parse_class_def(self):
        class_token = self.expect(TokenType.CLASS)
        name_token = self.expect(TokenType.IDENT)
        name = name_token.value
        self.skip_newlines()
        self.expect(TokenType.INDENT)
        self.skip_newlines()

        implements = None
        if self.match(TokenType.IMPLEMENTS):
            self.advance()
            impl_token = self.expect(TokenType.IDENT)
            implements = impl_token.value

            
        


        decorators = []
        fields = []
        methods = []

        while not self.match(TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()

            if self.match(TokenType.AT):
                decorators.append(self.parse_decorator())
                self.skip_newlines()
                continue

            if self.match(TokenType.PUBLIC, TokenType.PRIVATE):
                fields.extend(self.parse_field_declarations())
                self.skip_newlines()
                continue

            if self.is_method_definition():
                methods.append(self.parse_method_def())
                self.skip_newlines()
                continue

            self.error("Unexpected token inside class")

        self.expect(TokenType.DEDENT)

        return ClassDef(
            name,
            decorators,
            fields,
            methods,
            implements,
            class_token.line,
            class_token.col
        )
    
    def parse_protocol_def(self):
        """Parse: protocol Name INDENT methods DEDENT"""
        protocol_token = self.expect(TokenType.PROTOCOL)
        name_token = self.expect(TokenType.IDENT)
        name = name_token.value
        
        self.skip_newlines()
        self.expect(TokenType.INDENT)
        self.skip_newlines()
        
        methods = []
        
        while self.match(TokenType.FUN):
            self.advance()
            
            method_name_token = self.expect(TokenType.IDENT)
            method_name = method_name_token.value
            
            self.expect(TokenType.LPAREN)
            params = self.parse_params()
            self.expect(TokenType.RPAREN)
            
            return_type = None
            if self.match(TokenType.COLON):
                self.advance()
                type_token = self.expect(TokenType.IDENT)
                return_type = type_token.value
            
            methods.append(ProtocolMethod(method_name, params, return_type, 
                                        method_name_token.line, method_name_token.col))
            
            self.skip_newlines()
        
        self.expect(TokenType.DEDENT)
        
        return ProtocolDef(name, methods, protocol_token.line, protocol_token.col)





    def is_method_definition(self):
        return (
            self.match(TokenType.IDENT)
            and self.peek_token().type == TokenType.LPAREN
        )

    def parse_method_def(self):
            name_token = self.expect(TokenType.IDENT)
            name = name_token.value

            self.expect(TokenType.LPAREN)
            params = self.parse_params()
            self.expect(TokenType.RPAREN)

            # ✅ ADD THIS: Parse return type if present
            return_type = None
            if self.match(TokenType.COLON):
                
                type_token = self.expect(TokenType.IDENT)
                return_type = type_token.value

            self.skip_newlines()
            self.expect(TokenType.INDENT)

            body_stmts = self.parse_block()

            body = Block(
                body_stmts,
                name_token.line,
                name_token.col
            )

            self.expect(TokenType.DEDENT)

            return FunctionDef(
                name,
                params,
                body,
                return_type,  
                name_token.line,
                name_token.col
            )

    def parse_decorator(self):
        decorator_token = self.expect(TokenType.AT)
        name_token = self.expect(TokenType.IDENT)
        name = name_token.value

        args = {}

        if self.match(TokenType.LPAREN):
            self.advance()

            while not self.match(TokenType.RPAREN):
                key_token = self.expect(TokenType.IDENT)
                key = key_token.value

                self.expect(TokenType.ASSIGN)
                #debug
            
                # Parse value
                if self.match(TokenType.STRING):
                    value = self.current_token().value
                    self.advance()
                    args[key] = value
                elif self.match(TokenType.NUMBER):
                    value = self.current_token().value
                    self.advance()
                    args[key] = value
                elif self.match(TokenType.TRUE):
                    self.advance()
                    args[key] = True
                elif self.match(TokenType.FALSE):
                    self.advance()
                    args[key] = False
                elif self.match(TokenType.IDENT):
                    value = self.current_token().value
                    self.advance()
                    args[key] = value
                else:
                    self.error("Expected value in decorator argument")

                if not self.match(TokenType.RPAREN):
                    self.expect(TokenType.COMMA)

            self.expect(TokenType.RPAREN)

        return Decorator(
            name,
            args,
            decorator_token.line,
            decorator_token.col
        )

    def parse_field_declarations(self):
        visibility_token = self.current_token()

        if visibility_token.type == TokenType.PUBLIC:
            visibility = "public"
        else:
            visibility = "private"

        self.advance()

        self.skip_newlines()
        self.expect(TokenType.INDENT)
        self.skip_newlines()

        fields = []

        while self.match(TokenType.IDENT):
            field_name_token = self.expect(TokenType.IDENT)
            field_name = field_name_token.value

            self.expect(TokenType.COLON)

            field_type_token = self.expect(TokenType.IDENT)
            field_type = field_type_token.value

            fields.append(
                FieldDecl(
                    field_name,
                    field_type,
                    visibility,
                    field_name_token.line,
                    field_name_token.col
                )
            )

            self.skip_newlines()

        self.expect(TokenType.DEDENT)

        return fields

    def parse_function_def(self):
        fun_token = self.expect(TokenType.FUN)
        name_token = self.expect(TokenType.IDENT)
        name = name_token.value

        self.expect(TokenType.LPAREN)
        params = self.parse_params()
        self.expect(TokenType.RPAREN)

        # Parse return type if present
        return_type = None
        if self.match(TokenType.COLON):
            self.advance()
            type_token = self.expect(TokenType.IDENT)
            return_type = type_token.value

        self.skip_newlines()
        self.expect(TokenType.INDENT)

        body_stmts = self.parse_block()

        body = Block(
            body_stmts,
            fun_token.line,
            fun_token.col
        )

        self.expect(TokenType.DEDENT)

        return FunctionDef(
            name,
            params,
            body,
            return_type,
            fun_token.line,
            fun_token.col
        )





    def parse_task_def(self):
        task_token = self.expect(TokenType.TASK)
        name_token = self.expect(TokenType.IDENT)
        name = name_token.value

        self.expect(TokenType.LPAREN)
        params = self.parse_params()
        self.expect(TokenType.RPAREN)

        self.skip_newlines()
        self.expect(TokenType.INDENT)

        body_stmts = self.parse_block()

        body = Block(
            body_stmts,
            task_token.line,
            task_token.col
        )

        self.expect(TokenType.DEDENT)

        return TaskDef(
            name,
            params,
            body,
            task_token.line,
            task_token.col
        )

    def parse_params(self):
        params = []

        while not self.match(TokenType.RPAREN, TokenType.EOF):
            param_token = self.expect(TokenType.IDENT)
            param_name = param_token.value
            param_type = None

            # Check for type annotation
            if self.match(TokenType.COLON):
                self.advance()
                # Accept type keywords or custom type names
                if self.match(TokenType.INT):
                    param_type = 'int'
                    self.advance()
                elif self.match(TokenType.TEXT):
                    param_type = 'text'
                    self.advance()
                elif self.match(TokenType.BOOL):
                    param_type = 'bool'
                    self.advance()
                elif self.match(TokenType.FLOAT):
                    param_type = 'float'
                    self.advance()
                elif self.match(TokenType.VOID):
                    param_type = 'void'
                    self.advance()
                elif self.match(TokenType.IDENT):
                    type_token = self.current_token()
                    param_type = type_token.value
                    self.advance()
                else:
                    self.error("Expected type annotation")

            params.append((param_name, param_type))

            if not self.match(TokenType.RPAREN):
                self.expect(TokenType.COMMA)

        return params









    def parse_block(self):
        statements = []

        while not self.match(TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()

            if self.match(TokenType.DEDENT, TokenType.EOF):
                break

            stmt = self.parse_statement()

            if stmt:
                statements.append(stmt)

        return statements

    def parse_if_stmt(self):
        if_token = self.expect(TokenType.IF)
        condition = self.parse_expression()

        self.skip_newlines()
        self.expect(TokenType.INDENT)

        then_stmts = self.parse_block()

        then_body = Block(
            then_stmts,
            if_token.line,
            if_token.col
        )

        self.expect(TokenType.DEDENT)

        else_body = None

        if self.match(TokenType.ELSE):
            else_token = self.current_token()
            self.advance()

            self.skip_newlines()
            self.expect(TokenType.INDENT)

            else_stmts = self.parse_block()

            else_body = Block(
                else_stmts,
                else_token.line,
                else_token.col
            )

            self.expect(TokenType.DEDENT)

        return IfStmt(
            condition,
            then_body,
            else_body,
            if_token.line,
            if_token.col
        )

    def parse_while_stmt(self):
        while_token = self.expect(TokenType.WHILE)
        condition = self.parse_expression()

        self.skip_newlines()
        self.expect(TokenType.INDENT)

        body_stmts = self.parse_block()

        body = Block(
            body_stmts,
            while_token.line,
            while_token.col
        )

        self.expect(TokenType.DEDENT)

        return WhileStmt(
            condition,
            body,
            while_token.line,
            while_token.col
        )

    def parse_repeat_stmt(self):
        repeat_token = self.expect(TokenType.REPEAT)
        count = self.parse_expression()

        self.expect(TokenType.AS)

        var_token = self.expect(TokenType.IDENT)
        var = var_token.value

        self.skip_newlines()
        self.expect(TokenType.INDENT)

        body_stmts = self.parse_block()

        body = Block(
            body_stmts,
            repeat_token.line,
            repeat_token.col
        )

        self.expect(TokenType.DEDENT)

        return RepeatStmt(
            count,
            var,
            body,
            repeat_token.line,
            repeat_token.col
        )

    def parse_return_stmt(self):
        return_token = self.expect(TokenType.RETURN)

        if self.match(TokenType.NEWLINE, TokenType.DEDENT):
            value = None
        else:
            value = self.parse_expression()

        return ReturnStmt(
            value,
            return_token.line,
            return_token.col
        )

    def parse_expr_stmt(self):
        expr = self.parse_expression()

        if expr:
            return ExprStmt(expr, expr.line, expr.col)

        return None

    def parse_expression(self):
        left = self.parse_or_expr()

        if self.match(TokenType.ASSIGN):
            token = self.current_token()

            if not isinstance(left, (Identifier, MemberAccess, IndexAccess)):
                self.error("Invalid assignment target")

            self.advance()

            right = self.parse_expression()

            return Assignment(
                left,
                right,
                token.line,
                token.col
            )

        return left

    def parse_or_expr(self):
        left = self.parse_and_expr()

        while self.match(TokenType.OR):
            op_token = self.current_token()
            self.advance()

            right = self.parse_and_expr()

            left = BinaryOp(
                left,
                "or",
                right,
                op_token.line,
                op_token.col
            )

        return left

    def parse_and_expr(self):
        left = self.parse_not_expr()

        while self.match(TokenType.AND):
            op_token = self.current_token()
            self.advance()

            right = self.parse_not_expr()

            left = BinaryOp(
                left,
                "and",
                right,
                op_token.line,
                op_token.col
            )

        return left

    def parse_not_expr(self):
        if self.match(TokenType.NOT):
            token = self.current_token()
            self.advance()

            operand = self.parse_not_expr()

            return UnaryOp(
                "not",
                operand,
                token.line,
                token.col
            )

        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_additive()

        while True:
            if self.match(TokenType.EQ):
                token = self.current_token()
                self.advance()

                right = self.parse_additive()

                left = BinaryOp(
                    left,
                    "==",
                    right,
                    token.line,
                    token.col
                )

            elif self.match(TokenType.NE):
                token = self.current_token()
                self.advance()

                right = self.parse_additive()

                left = BinaryOp(
                    left,
                    "!=",
                    right,
                    token.line,
                    token.col
                )

            elif self.match(TokenType.LT):
                token = self.current_token()
                self.advance()

                right = self.parse_additive()

                left = BinaryOp(
                    left,
                    "<",
                    right,
                    token.line,
                    token.col
                )

            elif self.match(TokenType.GT):
                token = self.current_token()
                self.advance()

                right = self.parse_additive()

                left = BinaryOp(
                    left,
                    ">",
                    right,
                    token.line,
                    token.col
                )

            elif self.match(TokenType.LE):
                token = self.current_token()
                self.advance()

                right = self.parse_additive()

                left = BinaryOp(
                    left,
                    "<=",
                    right,
                    token.line,
                    token.col
                )

            elif self.match(TokenType.GE):
                token = self.current_token()
                self.advance()

                right = self.parse_additive()

                left = BinaryOp(
                    left,
                    ">=",
                    right,
                    token.line,
                    token.col
                )

            else:
                break

        return left

    def parse_additive(self):
        left = self.parse_multiplicative()

        while True:
            if self.match(TokenType.PLUS):
                token = self.current_token()
                self.advance()

                right = self.parse_multiplicative()

                left = BinaryOp(
                    left,
                    "+",
                    right,
                    token.line,
                    token.col
                )

            elif self.match(TokenType.MINUS):
                token = self.current_token()
                self.advance()

                right = self.parse_multiplicative()

                left = BinaryOp(
                    left,
                    "-",
                    right,
                    token.line,
                    token.col
                )

            else:
                break

        return left

    def parse_multiplicative(self):
        left = self.parse_power()

        while True:
            if self.match(TokenType.MULT):
                token = self.current_token()
                self.advance()

                right = self.parse_power()

                left = BinaryOp(
                    left,
                    "*",
                    right,
                    token.line,
                    token.col
                )

            elif self.match(TokenType.DIV):
                token = self.current_token()
                self.advance()

                right = self.parse_power()

                left = BinaryOp(
                    left,
                    "/",
                    right,
                    token.line,
                    token.col
                )

            elif self.match(TokenType.MOD):
                token = self.current_token()
                self.advance()

                right = self.parse_power()

                left = BinaryOp(
                    left,
                    "%",
                    right,
                    token.line,
                    token.col
                )

            elif self.match(TokenType.FLOORDIV):
                token = self.current_token()
                self.advance()

                right = self.parse_power()

                left = BinaryOp(
                    left,
                    "//",
                    right,
                    token.line,
                    token.col
                )

            else:
                break

        return left

    def parse_power(self):
        left = self.parse_unary()

        if self.match(TokenType.POWER):
            token = self.current_token()
            self.advance()

            right = self.parse_power()

            left = BinaryOp(
                left,
                "**",
                right,
                token.line,
                token.col
            )

        return left

    def parse_unary(self):
        if self.match(TokenType.PLUS):
            token = self.current_token()
            self.advance()

            operand = self.parse_unary()

            return UnaryOp(
                "+",
                operand,
                token.line,
                token.col
            )

        if self.match(TokenType.MINUS):
            token = self.current_token()
            self.advance()

            operand = self.parse_unary()

            return UnaryOp(
                "-",
                operand,
                token.line,
                token.col
            )

        return self.parse_postfix()

    def parse_postfix(self):
        left = self.parse_primary()

        while True:
            if self.match(TokenType.LPAREN):
                left = self.parse_call(left)

            elif self.match(TokenType.DOT):
                self.advance()

                member_token = self.expect(TokenType.IDENT)

                left = MemberAccess(
                    left,
                    member_token.value,
                    member_token.line,
                    member_token.col
                )

            elif self.match(TokenType.LBRACKET):
                self.advance()
                index_expr = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                left = IndexAccess(left, index_expr, left.line, left.col)

            else:
                break

        return left

    def parse_call(self, func_expr):
        self.expect(TokenType.LPAREN)

        args = []

        while not self.match(TokenType.RPAREN):
            args.append(self.parse_expression())

            if not self.match(TokenType.RPAREN):
                self.expect(TokenType.COMMA)

        self.expect(TokenType.RPAREN)

        return CallExpr(
            func_expr,
            args,
            func_expr.line,
            func_expr.col
        )

    def parse_primary(self):
        #map expresion: expr from var in iterable [where condition]
        if self.match(TokenType.MAP):
            map_token = self.current_token()
            self.advance()
            expr = self.parse_comparison()
            self.expect(TokenType.FROM)
            var_token = self.expect(TokenType.IDENT)
            var = var_token.value
            self.expect(TokenType.IN)
            iterable = self.parse_comparison()
            condition = None
            if self.match(TokenType.WHERE):
                self.advance()
                condition = self.parse_comparison()
            return MapExpr(expr, var, iterable, condition, map_token.line, map_token.col)



        #Field access: @fieldname
        if self.match(TokenType.AT):
            at_token = self.current_token()
            self.advance()
            if not self.match(TokenType.IDENT):
                self.error("Expected field name after @")
            field_token = self.current_token()
            self.advance()

            return MemberAccess(
                Identifier("this", at_token.line, at_token.col),
                field_token.value,
                at_token.line,
                at_token.col)

        
        

        
        if self.match(TokenType.NUMBER):
            token = self.current_token()
            self.advance()

            return NumberLiteral(
                token.value,
                token.line,
                token.col
            )

        if self.match(TokenType.STRING):
            token = self.current_token()
            self.advance()

            if '{' in token.value and '}' in token.value:
                parts = self.parse_string_interpolation(token.value, token.line, token.col)
                return StringInterpolation(parts, token.line, token.col)
            else:
                return StringLiteral(
                    token.value,
                    token.line,
                    token.col
                )

        if self.match(TokenType.TRUE):
            token = self.current_token()
            self.advance()

            return BoolLiteral(
                True,
                token.line,
                token.col
            )

        if self.match(TokenType.FALSE):
            token = self.current_token()
            self.advance()

            return BoolLiteral(
                False,
                token.line,
                token.col
            )

        if self.match(TokenType.ARRAY):
            self.advance()
            self.expect(TokenType.LPAREN)
            elements = []

            while not self.match(TokenType.RPAREN):
                elements.append(self.parse_comparison())
                if not self.match(TokenType.RPAREN):
                    self.expect(TokenType.COMMA)

            self.expect(TokenType.RPAREN)
            return ArrayLiteral(elements)

        if self.match(TokenType.MAP):
            self.advance()
            self.expect(TokenType.LPAREN)
            pairs = []

            while not self.match(TokenType.RPAREN):
                key_token = self.expect(TokenType.IDENT)
                key = key_token.value
                self.expect(TokenType.ASSIGN)
                value = self.parse_expression()
                pairs.append((key, value))

                if not self.match(TokenType.RPAREN):
                    self.expect(TokenType.COMMA)

            self.expect(TokenType.RPAREN)
            return MapLiteral(pairs)

        if self.match(TokenType.WAIT):
            wait_token = self.current_token()
            self.advance()
            task_call = self.parse_postfix()
            return WaitExpr(task_call, wait_token.line, wait_token.col)

        if self.match(TokenType.IDENT):
            token = self.current_token()
            self.advance()

            return Identifier(
                token.value,
                token.line,
                token.col
            )

        if self.match(TokenType.LPAREN):
            self.advance()

            expr = self.parse_expression()

            self.expect(TokenType.RPAREN)

            return expr

        token = self.current_token()

        self.error(f"Unexpected token: {token.type}")

    def parse_string_interpolation(self, string_value, line, col):
        parts = []
        i = 0

        while i < len(string_value):
            brace_pos = string_value.find('{', i)

            if brace_pos == -1:
                if i < len(string_value):
                    text = string_value[i:]
                    text = text.replace(r'\{', '{').replace(r'\}', '}')
                    parts.append(StringPart("text", text, line, col))
                break

            if brace_pos > 0 and string_value[brace_pos - 1] == '\\':
                i = brace_pos + 1
                continue

            if brace_pos > i:
                text = string_value[i:brace_pos]
                text = text.replace(r'\{', '{').replace(r'\}', '}')
                parts.append(StringPart("text", text, line, col))

            close_brace = string_value.find('}', brace_pos)
            if close_brace == -1:
                raise NexvoidRuntimeError(f"Unclosed {{ in string at line {line}")

            expr_str = string_value[brace_pos + 1:close_brace]

            try:
                lexer = NexvoidLexer(expr_str)
                tokens = lexer.tokenize()
                parser = NexvoidParser(tokens)
                expr_node = parser.parse_expression()
                parts.append(StringPart("expr", expr_node, line, col))
            except Exception as e:
                raise NexvoidRuntimeError(f"Bad expression in interpolation: {expr_str}")

            i = close_brace + 1

        return parts
                 



