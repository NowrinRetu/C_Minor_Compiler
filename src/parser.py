from tokens import TokenKind
from ast_nodes import (
    SourceSpan, Program, Parameter, FunctionDecl, Block, VarDecl,
    ReturnStmt, BreakStmt, ContinueStmt, ExprStmt,
    IfStmt, WhileStmt, ForStmt, Assignment, Binary, Unary,
    IntegerLiteral, Identifier, Call
)
from diagnostics import ParserError


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    # Return current token
    def current(self):
        return self.tokens[self.position]

    # Move to the next token
    def advance(self):
        token = self.current()

        if token.kind != TokenKind.EOF:
            self.position += 1

        return token

    # Check whether current token matches
    def match(self, kind):
        if self.current().kind == kind:
            self.advance()
            return True

        return False

    # Expect a specific token
    def expect(self, kind, message):
        if self.current().kind == kind:
            return self.advance()

        token = self.current()
        raise ParserError(message, token.line, token.column)

    # Parse complete program
    def parse_program(self):
        declarations = []
        start = self.current()

        while self.current().kind != TokenKind.EOF:
            declarations.append(self.parse_external())

        end = self.current()

        return Program(
            span=SourceSpan(
                start.line,
                start.column,
                end.line,
                end.column
            ),
            declarations=declarations
        )

    # Parse function declaration or definition
    def parse_external(self):

        if self.current().kind not in (
            TokenKind.INT,
            TokenKind.VOID
        ):
            token = self.current()
            raise ParserError(
                "Expected function return type",
                token.line,
                token.column
            )

        return_token = self.advance()
        return_type = return_token.lexeme

        name = self.expect(
            TokenKind.IDENTIFIER,
            "Expected function name"
        )

        self.expect(
            TokenKind.LPAREN,
            "Expected '(' after function name"
        )

        parameters = self.parse_parameters()

        self.expect(
            TokenKind.RPAREN,
            "Expected ')' after parameters"
        )

        # Function declaration
        if self.current().kind == TokenKind.SEMICOLON:
            end = self.advance()

            return FunctionDecl(
                span=SourceSpan(
                    return_token.line,
                    return_token.column,
                    end.line,
                    end.column + 1
                ),
                return_type=return_type,
                name=name.lexeme,
                params=parameters,
                body=None
            )

        # Function definition requires parameter names
        for parameter in parameters:
            if parameter.name is None:
                raise ParserError(
                    "Parameter name required in function definition",
                    parameter.span.line,
                    parameter.span.column
                )

        body = self.parse_block()

        return FunctionDecl(
            span=SourceSpan(
                return_token.line,
                return_token.column,
                body.span.end_line,
                body.span.end_column
            ),
            return_type=return_type,
            name=name.lexeme,
            params=parameters,
            body=body
        )

    # Parse function parameters
    def parse_parameters(self):

        parameters = []

        # void means no parameters
        if self.match(TokenKind.VOID):
            return parameters

        # Empty parameter list
        if self.current().kind == TokenKind.RPAREN:
            return parameters

        while True:

            type_token = self.expect(
                TokenKind.INT,
                "Expected parameter type 'int'"
            )

            parameter_name = None

            if self.current().kind == TokenKind.IDENTIFIER:
                name_token = self.advance()
                parameter_name = name_token.lexeme

                parameter_span = SourceSpan(
                    name_token.line,
                    name_token.column,
                    name_token.line,
                    name_token.column + len(name_token.lexeme)
                )
            else:
                parameter_span = SourceSpan(
                    type_token.line,
                    type_token.column,
                    type_token.line,
                    type_token.column + len(type_token.lexeme)
                )

            parameters.append(
                Parameter(
                    span=parameter_span,
                    type_name="int",
                    name=parameter_name
                )
            )

            if not self.match(TokenKind.COMMA):
                break

        return parameters

    # Parse a block of statements
    def parse_block(self):

        start = self.expect(
            TokenKind.LBRACE,
            "Expected '{'"
        )

        statements = []

        while self.current().kind not in (
            TokenKind.RBRACE,
            TokenKind.EOF
        ):
            if self.current().kind == TokenKind.INT:
                statements.append(self.parse_local_decl())
            else:
                statements.append(self.parse_statement())

        end = self.expect(
            TokenKind.RBRACE,
            "Expected '}'"
        )

        return Block(
            span=SourceSpan(
                start.line,
                start.column,
                end.line,
                end.column + 1
            ),
            statements=statements
        )

    # Parse local variable declaration
    def parse_local_decl(self):

        start = self.expect(
            TokenKind.INT,
            "Expected 'int'"
        )

        name = self.expect(
            TokenKind.IDENTIFIER,
            "Expected variable name"
        )

        initializer = None

        if self.match(TokenKind.ASSIGN):
            initializer = self.parse_assignment_expr()

        end = self.expect(
            TokenKind.SEMICOLON,
            "Expected ';' after variable declaration"
        )

        return VarDecl(
            span=SourceSpan(
                start.line,
                start.column,
                end.line,
                end.column + 1
            ),
            name=name.lexeme,
            initializer=initializer
        )
        # Parse statements
    def parse_statement(self):

        if self.current().kind == TokenKind.RETURN:
            return self.parse_return_stmt()

        if self.current().kind == TokenKind.LBRACE:
            return self.parse_block()

        if self.current().kind == TokenKind.IF:
            return self.parse_if_stmt()

        if self.current().kind == TokenKind.WHILE:
            return self.parse_while_stmt()

        if self.current().kind == TokenKind.FOR:
            return self.parse_for_stmt()

        if self.current().kind == TokenKind.BREAK:
            token = self.advance()
            end = self.expect(
                TokenKind.SEMICOLON,
                "Expected ';'"
            )

            return BreakStmt(
                span=SourceSpan(
                    token.line,
                    token.column,
                    end.line,
                    end.column + 1
                )
            )

        if self.current().kind == TokenKind.CONTINUE:
            token = self.advance()
            end = self.expect(
                TokenKind.SEMICOLON,
                "Expected ';'"
            )

            return ContinueStmt(
                span=SourceSpan(
                    token.line,
                    token.column,
                    end.line,
                    end.column + 1
                )
            )

        return self.parse_expr_stmt()

    # Parse return statement
    def parse_return_stmt(self):

        start = self.expect(
            TokenKind.RETURN,
            "Expected 'return'"
        )

        expression = None

        if self.current().kind != TokenKind.SEMICOLON:
            expression = self.parse_assignment_expr()

        end = self.expect(
            TokenKind.SEMICOLON,
            "Expected ';' after return statement"
        )

        return ReturnStmt(
            span=SourceSpan(
                start.line,
                start.column,
                end.line,
                end.column + 1
            ),
            expression=expression
        )

    # Parse if-else statement
    def parse_if_stmt(self):

        start = self.expect(
            TokenKind.IF,
            "Expected 'if'"
        )

        self.expect(
            TokenKind.LPAREN,
            "Expected '(' after if"
        )

        condition = self.parse_assignment_expr()

        self.expect(
            TokenKind.RPAREN,
            "Expected ')' after condition"
        )

        then_branch = self.parse_statement()
        else_branch = None

        if self.match(TokenKind.ELSE):
            else_branch = self.parse_statement()

        final_branch = (
            else_branch if else_branch is not None
            else then_branch
        )

        return IfStmt(
            span=SourceSpan(
                start.line,
                start.column,
                final_branch.span.end_line,
                final_branch.span.end_column
            ),
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch
        )

    # Parse while loop
    def parse_while_stmt(self):

        start = self.expect(
            TokenKind.WHILE,
            "Expected 'while'"
        )

        self.expect(
            TokenKind.LPAREN,
            "Expected '(' after while"
        )

        condition = self.parse_assignment_expr()

        self.expect(
            TokenKind.RPAREN,
            "Expected ')' after condition"
        )

        body = self.parse_statement()

        return WhileStmt(
            span=SourceSpan(
                start.line,
                start.column,
                body.span.end_line,
                body.span.end_column
            ),
            condition=condition,
            body=body
        )

    # Parse for loop
    def parse_for_stmt(self):

        start = self.expect(
            TokenKind.FOR,
            "Expected 'for'"
        )

        self.expect(
            TokenKind.LPAREN,
            "Expected '(' after for"
        )

        initializer = None
        condition = None
        update = None

        # Parse initializer
        if self.current().kind == TokenKind.INT:
            initializer = self.parse_local_decl()

        elif self.current().kind != TokenKind.SEMICOLON:
            initializer = self.parse_assignment_expr()

            self.expect(
                TokenKind.SEMICOLON,
                "Expected ';' after for initializer"
            )

        else:
            self.advance()

        # Parse condition
        if self.current().kind != TokenKind.SEMICOLON:
            condition = self.parse_assignment_expr()

        self.expect(
            TokenKind.SEMICOLON,
            "Expected ';' after for condition"
        )

        # Parse update
        if self.current().kind != TokenKind.RPAREN:
            update = self.parse_assignment_expr()

        self.expect(
            TokenKind.RPAREN,
            "Expected ')' after for clauses"
        )

        body = self.parse_statement()

        return ForStmt(
            span=SourceSpan(
                start.line,
                start.column,
                body.span.end_line,
                body.span.end_column
            ),
            initializer=initializer,
            condition=condition,
            update=update,
            body=body
        )

    # Parse expression statement
    def parse_expr_stmt(self):

        if self.current().kind == TokenKind.SEMICOLON:
            token = self.advance()

            return ExprStmt(
                span=SourceSpan(
                    token.line,
                    token.column,
                    token.line,
                    token.column + 1
                ),
                expression=None
            )

        expression = self.parse_assignment_expr()

        end = self.expect(
            TokenKind.SEMICOLON,
            "Expected ';' after expression"
        )

        return ExprStmt(
            span=SourceSpan(
                expression.span.line,
                expression.span.column,
                end.line,
                end.column + 1
            ),
            expression=expression
        )

    # Parse assignment expression
    def parse_assignment_expr(self):

        left = self.parse_logical_or()

        if self.match(TokenKind.ASSIGN):
            value = self.parse_assignment_expr()

            return Assignment(
                span=SourceSpan(
                    left.span.line,
                    left.span.column,
                    value.span.end_line,
                    value.span.end_column
                ),
                target=left,
                value=value
            )

        return left
        # Parse logical OR expression
    def parse_logical_or(self):

        left = self.parse_logical_and()

        while self.match(TokenKind.OR):

            right = self.parse_logical_and()

            left = Binary(
                span=SourceSpan(
                    left.span.line,
                    left.span.column,
                    right.span.end_line,
                    right.span.end_column
                ),
                left=left,
                operator="||",
                right=right
            )

        return left

    # Parse logical AND expression
    def parse_logical_and(self):

        left = self.parse_equality()

        while self.match(TokenKind.AND):

            right = self.parse_equality()

            left = Binary(
                span=SourceSpan(
                    left.span.line,
                    left.span.column,
                    right.span.end_line,
                    right.span.end_column
                ),
                left=left,
                operator="&&",
                right=right
            )

        return left

    # Parse equality expression
    def parse_equality(self):

        left = self.parse_relational()

        while self.current().kind in (
            TokenKind.EQUAL,
            TokenKind.NOT_EQUAL
        ):

            operator_token = self.advance()
            operator = operator_token.lexeme

            right = self.parse_relational()

            left = Binary(
                span=SourceSpan(
                    left.span.line,
                    left.span.column,
                    right.span.end_line,
                    right.span.end_column
                ),
                left=left,
                operator=operator,
                right=right
            )

        return left

    # Parse relational expression
    def parse_relational(self):

        left = self.parse_additive()

        while self.current().kind in (
            TokenKind.LESS,
            TokenKind.LESS_EQUAL,
            TokenKind.GREATER,
            TokenKind.GREATER_EQUAL
        ):

            operator_token = self.advance()
            operator = operator_token.lexeme

            right = self.parse_additive()

            left = Binary(
                span=SourceSpan(
                    left.span.line,
                    left.span.column,
                    right.span.end_line,
                    right.span.end_column
                ),
                left=left,
                operator=operator,
                right=right
            )

        return left

    # Parse additive expression
    def parse_additive(self):

        left = self.parse_multiplicative()

        while self.current().kind in (
            TokenKind.PLUS,
            TokenKind.MINUS
        ):

            operator_token = self.advance()
            operator = operator_token.lexeme

            right = self.parse_multiplicative()

            left = Binary(
                span=SourceSpan(
                    left.span.line,
                    left.span.column,
                    right.span.end_line,
                    right.span.end_column
                ),
                left=left,
                operator=operator,
                right=right
            )

        return left

    # Parse multiplicative expression
    def parse_multiplicative(self):

        left = self.parse_unary()

        while self.current().kind in (
            TokenKind.MULTIPLY,
            TokenKind.DIVIDE,
            TokenKind.MODULO
        ):

            operator_token = self.advance()
            operator = operator_token.lexeme

            right = self.parse_unary()

            left = Binary(
                span=SourceSpan(
                    left.span.line,
                    left.span.column,
                    right.span.end_line,
                    right.span.end_column
                ),
                left=left,
                operator=operator,
                right=right
            )

        return left

    # Parse unary expression
    def parse_unary(self):

        if self.current().kind in (
            TokenKind.PLUS,
            TokenKind.MINUS,
            TokenKind.NOT
        ):

            operator_token = self.advance()
            operator = operator_token.lexeme

            operand = self.parse_unary()

            return Unary(
                span=SourceSpan(
                    operator_token.line,
                    operator_token.column,
                    operand.span.end_line,
                    operand.span.end_column
                ),
                operator=operator,
                operand=operand
            )

        return self.parse_primary()

    # Parse primary expression
    def parse_primary(self):

        token = self.current()

        # Integer literal
        if token.kind == TokenKind.INTEGER:
            self.advance()

            return IntegerLiteral(
                span=SourceSpan(
                    token.line,
                    token.column,
                    token.line,
                    token.column + len(token.lexeme)
                ),
                value=int(token.lexeme)
            )

        # Identifier or function call
        if token.kind == TokenKind.IDENTIFIER:
            self.advance()

            identifier = Identifier(
                span=SourceSpan(
                    token.line,
                    token.column,
                    token.line,
                    token.column + len(token.lexeme)
                ),
                name=token.lexeme
            )

            if self.match(TokenKind.LPAREN):

                arguments = []

                if self.current().kind != TokenKind.RPAREN:
                    arguments.append(
                        self.parse_assignment_expr()
                    )

                    while self.match(TokenKind.COMMA):
                        arguments.append(
                            self.parse_assignment_expr()
                        )

                end = self.expect(
                    TokenKind.RPAREN,
                    "Expected ')'"
                )

                return Call(
                    span=SourceSpan(
                        token.line,
                        token.column,
                        end.line,
                        end.column + 1
                    ),
                    name=token.lexeme,
                    arguments=arguments
                )

            return identifier

        # Parenthesized expression
        if self.match(TokenKind.LPAREN):

            expression = self.parse_assignment_expr()

            self.expect(
                TokenKind.RPAREN,
                "Expected ')'"
            )

            return expression

        raise ParserError(
            "Expected an expression",
            token.line,
            token.column
        )