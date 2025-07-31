class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"

class Statement(ASTNode):
    pass

class VariableDeclaration(Statement):
    def __init__(self, identifier, var_type=None, initializer=None):
        self.identifier = identifier
        self.var_type = var_type
        self.initializer = initializer

    def __repr__(self):
        if self.initializer:
            return f"VariableDeclaration(identifier='{self.identifier}', type='{self.var_type}', initializer={self.initializer})"
        return f"VariableDeclaration(identifier='{self.identifier}', type='{self.var_type}')"

class AssignmentStatement(Statement):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    def __repr__(self):
        return f"AssignmentStatement(identifier='{self.identifier}', expression={self.expression})"

class Expression(ASTNode):
    pass

class IdentifierExpression(Expression):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"IdentifierExpression('{self.name}')"

class LiteralExpression(Expression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"LiteralExpression({self.value})"

class BinaryOperation(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryOperation({self.left}, '{self.operator}', {self.right})"