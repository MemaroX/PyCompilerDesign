class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"

class Statement(ASTNode):
    pass

class Expression(ASTNode):
    pass

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