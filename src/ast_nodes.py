
from dataclasses import dataclass
from typing import Optional


# Stores the position of a node in the source code
@dataclass
class SourceSpan:
    line: int
    column: int
    end_line: int
    end_column: int


# Base class for all AST nodes
@dataclass
class ASTNode:
    span: SourceSpan


# Complete program
@dataclass
class Program(ASTNode):
    declarations: list


# Function declaration or definition
@dataclass
class FunctionDecl(ASTNode):
    return_type: str
    name: str
    params: list
    body: Optional["Block"] = None


# Function parameter
@dataclass
class Parameter(ASTNode):
    type_name: str
    name: Optional[str] = None


# Variable declaration
@dataclass
class VarDecl(ASTNode):
    name: str
    initializer: Optional["Expression"] = None


# A block containing statements
@dataclass
class Block(ASTNode):
    statements: list


# Base class for expressions
@dataclass
class Expression(ASTNode):
    pass


# Integer literal
@dataclass
class IntegerLiteral(Expression):
    value: int


# Variable name
@dataclass
class Identifier(Expression):
    name: str


# Function call
@dataclass
class Call(Expression):
    name: str
    arguments: list


# Unary expression: -a, +a, !a
@dataclass
class Unary(Expression):
    operator: str
    operand: Expression


# Binary expression: a + b, a < b
@dataclass
class Binary(Expression):
    left: Expression
    operator: str
    right: Expression


# Assignment expression: a = b
@dataclass
class Assignment(Expression):
    target: Expression
    value: Expression


# Base class for statements
@dataclass
class Statement(ASTNode):
    pass


# Expression statement
@dataclass
class ExprStmt(Statement):
    expression: Optional[Expression] = None


# If-else statement
@dataclass
class IfStmt(Statement):
    condition: Expression
    then_branch: Statement
    else_branch: Optional[Statement] = None


# While loop
@dataclass
class WhileStmt(Statement):
    condition: Expression
    body: Statement


# For loop
@dataclass
class ForStmt(Statement):
    initializer: Optional[ASTNode]
    condition: Optional[Expression]
    update: Optional[Expression]
    body: Statement


# Break statement
@dataclass
class BreakStmt(Statement):
    pass


# Continue statement
@dataclass
class ContinueStmt(Statement):
    pass


# Return statement
@dataclass
class ReturnStmt(Statement):
    expression: Optional[Expression] = None
