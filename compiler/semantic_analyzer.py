from compiler.ast_nodes import Program, VariableDeclaration, AssignmentStatement, LiteralExpression, BinaryOperation, IdentifierExpression

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
        # Use the declared type from the AST node
        declared_type = node.var_type if node.var_type else 'int' # Default to 'int' if no type specified (for 'let' declarations)
        self.current_scope.define(node.identifier, {'type': declared_type, 'declared': True})
        if node.initializer:
            # Visit the initializer to get its type/value
            initializer_value = self.visit(node.initializer)
            # Basic type check: ensure initializer is compatible with declared type
            if declared_type == 'int':
                if not isinstance(initializer_value, (int, float)):
                    raise ValueError(f"Type mismatch: Cannot assign {type(initializer_value).__name__} to {declared_type} variable '{node.identifier}'")
            # Add more type checks for other types as needed

    def visit_AssignmentStatement(self, node: AssignmentStatement):
        symbol_info = self.current_scope.resolve(node.identifier)
        if not symbol_info:
            raise ValueError(f"Undeclared variable: '{node.identifier}'")
        
        # Visit the expression to get its type/value
        expression_value = self.visit(node.expression)
        # Basic type check: ensure expression is compatible with variable's type
        assigned_to_type = symbol_info['type']
        if assigned_to_type == 'int':
            if not isinstance(expression_value, (int, float)):
                raise ValueError(f"Type mismatch: Cannot assign {type(expression_value).__name__} to {assigned_to_type} variable '{node.identifier}'")
        # Add more type checks for other types as needed

    def visit_LiteralExpression(self, node: LiteralExpression):
        # Return the actual value of the literal for type checking
        return node.value

    def visit_IdentifierExpression(self, node: IdentifierExpression):
        # Resolve the identifier's type from the symbol table
        symbol_info = self.current_scope.resolve(node.name)
        if not symbol_info:
            raise ValueError(f"Undeclared variable: '{node.name}'")
        # For now, return a placeholder value based on its type for type checking
        # In a real compiler, this would return the actual type.
        if symbol_info['type'] == 'int':
            return 0 # Placeholder for int
        return None # Placeholder for other types

    def visit_BinaryOperation(self, node: BinaryOperation):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)

        # Basic type checking for binary operations
        if not isinstance(left_value, (int, float)) or not isinstance(right_value, (int, float)):
            raise ValueError(f"Type mismatch: Binary operation '{node.operator}' requires numeric operands.")
        
        # For now, return a placeholder result for the operation
        if node.operator == '+':
            return left_value + right_value
        elif node.operator == '-':
            return left_value - right_value
        elif node.operator == '*':
            return left_value * right_value
        elif node.operator == '/':
            if right_value == 0:
                raise ValueError("Division by zero.")
            return left_value / right_value
        
        return None # Placeholder for other operations
