from compiler.ast_nodes import Program, VariableDeclaration, AssignmentStatement, LiteralExpression, BinaryOperation

class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, name, symbol_info):
        if name in self.symbols:
            raise ValueError(f"Redeclaration of variable '{name}' in the same scope.")
        self.symbols[name] = symbol_info

    def resolve(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.resolve(name)
        return None

class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope

    def enter_scope(self):
        new_scope = SymbolTable(parent=self.current_scope)
        self.current_scope = new_scope

    def exit_scope(self):
        if self.current_scope.parent is None:
            raise Exception("Cannot exit global scope.")
        self.current_scope = self.current_scope.parent

    def analyze(self, ast):
        self.visit(ast)

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method")

    def visit_Program(self, node: Program):
        self.enter_scope()
        for statement in node.statements:
            self.visit(statement)
        self.exit_scope()

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        # For now, we'll assume all variables are of a generic 'int' type.
        # In a more advanced compiler, we'd infer or parse the type.
        self.current_scope.define(node.identifier, {'type': 'int', 'declared': True})
        if node.initializer:
            self.visit(node.initializer)
            # Basic type check: ensure initializer is compatible with 'int'
            # This is a placeholder; actual type checking would be more complex.
            if isinstance(node.initializer, LiteralExpression) and not isinstance(node.initializer.value, (int, float)):
                raise ValueError(f"Type mismatch: Cannot assign {type(node.initializer.value).__name__} to int variable '{node.identifier}'")

    def visit_AssignmentStatement(self, node: AssignmentStatement):
        symbol_info = self.current_scope.resolve(node.identifier)
        if not symbol_info:
            raise ValueError(f"Undeclared variable: '{node.identifier}'")
        
        self.visit(node.expression)
        # Basic type check: ensure expression is compatible with variable's type
        # This is a placeholder; actual type checking would be more complex.
        if symbol_info['type'] == 'int':
            if isinstance(node.expression, LiteralExpression) and not isinstance(node.expression.value, (int, float)):
                raise ValueError(f"Type mismatch: Cannot assign {type(node.expression.value).__name__} to int variable '{node.identifier}'")

    def visit_LiteralExpression(self, node: LiteralExpression):
        # For now, we just visit the literal. Type information could be returned here.
        pass

    def visit_BinaryOperation(self, node: BinaryOperation):
        self.visit(node.left)
        self.visit(node.right)
        # Basic type checking for binary operations would go here.
        # For example, ensuring both operands are numbers for arithmetic ops.
        pass
