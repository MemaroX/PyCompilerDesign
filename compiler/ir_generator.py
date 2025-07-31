from typing import List
from compiler.ast_nodes import Program, VariableDeclaration, AssignmentStatement, LiteralExpression, BinaryOperation, IdentifierExpression

class TACInstruction:
    def __init__(self, op: str, arg1: str = None, arg2: str = None, result: str = None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __repr__(self):
        if self.op == 'ASSIGN':
            return f"{self.result} = {self.arg1}"
        elif self.op in ['ADD', 'SUB', 'MUL', 'DIV']:
            return f"{self.result} = {self.arg1} {self.op_symbol()} {self.arg2}"
        elif self.op == 'GOTO':
            return f"goto {self.result}"
        elif self.op == 'IF_FALSE_GOTO':
            return f"if_false {self.arg1} goto {self.result}"
        elif self.op == 'PARAM':
            return f"param {self.arg1}"
        elif self.op == 'CALL':
            if self.result:
                return f"{self.result} = call {self.arg1}, {self.arg2}"
            return f"call {self.arg1}, {self.arg2}"
        return f"{self.op} {self.arg1 or ''} {self.arg2 or ''} {self.result or ''}".strip()

    def op_symbol(self):
        symbols = {'ADD': '+', 'SUB': '-', 'MUL': '*', 'DIV': '/'}
        return symbols.get(self.op, self.op)

class IRGenerator:
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_counter = 0
        self.label_counter = 0

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, instruction: TACInstruction):
        self.instructions.append(instruction)

    def generate(self, ast: Program) -> List[TACInstruction]:
        self.visit(ast)
        return self.instructions

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"IR generation not implemented for {type(node).__name__}")

    def visit_Program(self, node: Program):
        for statement in node.statements:
            self.visit(statement)

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        # For typed declarations, we might emit a special instruction or just use the identifier
        # For now, we'll just handle the initializer if present.
        if node.initializer:
            initializer_val = self.visit(node.initializer)
            self.emit(TACInstruction('ASSIGN', initializer_val, result=node.identifier))
        else:
            # For declarations without initializer (e.g., 'int x;'), no TAC is strictly needed
            # unless we want to initialize to a default value.
            pass

    def visit_AssignmentStatement(self, node: AssignmentStatement):
        expr_temp = self.visit(node.expression)
        self.emit(TACInstruction('ASSIGN', expr_temp, result=node.identifier))

    def visit_LiteralExpression(self, node: LiteralExpression):
        return node.value

    def visit_IdentifierExpression(self, node: IdentifierExpression) -> str:
        return node.name

    def visit_BinaryOperation(self, node: BinaryOperation) -> str:
        left_temp = self.visit(node.left)
        right_temp = self.visit(node.right)
        result_temp = self.new_temp()
        self.emit(TACInstruction(node.operator.upper(), left_temp, right_temp, result=result_temp))
        return result_temp
