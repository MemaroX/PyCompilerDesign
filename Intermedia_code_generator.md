# Intermediate Code Generation (ICG) with Three-Address Code (TAC)

## 1. Introduction to Intermediate Code Generation

Intermediate Code Generation (ICG) is a crucial phase in the compilation process, acting as a bridge between the front-end (lexical analysis, parsing, semantic analysis) and the back-end (optimization, code generation). Its primary purpose is to transform the Abstract Syntax Tree (AST), which is a high-level, language-specific representation, into a lower-level, machine-independent intermediate representation (IR).

**Why ICG is Important:**

*   **Machine Independence:** The IR is not tied to any specific machine architecture, allowing the compiler to be portable across different platforms.
*   **Optimization Opportunities:** The IR provides a suitable level of abstraction for applying various compiler optimizations (e.g., dead code elimination, common subexpression elimination) before generating final machine code.
*   **Simplifies Code Generation:** The back-end can focus on translating the simplified IR into machine code, rather than directly dealing with the complexities of the source language's AST.

## 2. Three-Address Code (TAC)

Three-Address Code (TAC) is a common form of intermediate representation. It is characterized by instructions that have at most three operands (two sources and one destination). Each TAC instruction typically represents a single elementary operation.

**Characteristics of TAC:**

*   **Simple Structure:** Each instruction is straightforward, making it easy to generate, analyze, and optimize.
*   **Explicit Temporaries:** Intermediate results are stored in explicitly named temporary variables, which simplifies data flow analysis.
*   **Linear Sequence:** Instructions are arranged in a linear sequence, similar to assembly code.

**Examples of TAC Instructions:**

| Operation           | TAC Format           | Description                                     |
| :------------------ | :------------------- | :---------------------------------------------- |
| Assignment          | `x = y`              | Assigns the value of `y` to `x`.                |
| Binary Operation    | `x = y op z`         | Performs `op` on `y` and `z`, stores in `x`.    |
| Unary Operation     | `x = op y`           | Performs `op` on `y`, stores in `x`.            |
| Conditional Jump    | `if x goto L`        | Jumps to label `L` if `x` is true.              |
| Unconditional Jump  | `goto L`             | Jumps unconditionally to label `L`.             |
| Function Call       | `param x`            | Passes `x` as a parameter.                      |
|                     | `call P, n`          | Calls procedure `P` with `n` parameters.        |
|                     | `x = call P, n`      | Calls `P`, stores return value in `x`.          |
| Indexed Assignment  | `x = y[i]`           | Assigns `y[i]` to `x`.                          |
|                     | `x[i] = y`           | Assigns `y` to `x[i]`.                          |

## 3. Design of TAC Structures

We will represent TAC instructions using a simple class or a named tuple. For flexibility and clarity, a class is often preferred.

```python
# compiler/ir_generator.py (or a new tac_structures.py)

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
        # Add more representations as needed for other operations

    def op_symbol(self):
        # Helper for __repr__ to get actual symbols for binary ops
        symbols = {'ADD': '+', 'SUB': '-', 'MUL': '*', 'DIV': '/'}
        return symbols.get(self.op, self.op)

# Example usage:
# tac_list = []
# tac_list.append(TACInstruction('ASSIGN', '10', result='t1'))
# tac_list.append(TACInstruction('ASSIGN', '20', result='t2'))
# tac_list.append(TACInstruction('ADD', 't1', 't2', result='t3'))
# tac_list.append(TACInstruction('ASSIGN', 't3', result='x'))
```

## 4. `IRGenerator` Class Design

The `IRGenerator` class will be responsible for traversing the Abstract Syntax Tree (AST) and emitting a sequence of `TACInstruction` objects. It will act as a visitor over the AST.

```python
# compiler/ir_generator.py

from typing import List
from compiler.ast_nodes import Program, VariableDeclaration, AssignmentStatement, LiteralExpression, BinaryOperation
from compiler.semantic_analyzer import SymbolTable # We'll need access to symbol info

class IRGenerator:
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_counter = 0
        self.label_counter = 0
        # We might pass the symbol table from semantic analysis here
        # self.symbol_table = symbol_table

    def new_temp(self) -> str:
        """Generates a new unique temporary variable name."""
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self) -> str:
        """Generates a new unique label name."""
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, instruction: TACInstruction):
        """Adds a TAC instruction to the list."""
        self.instructions.append(instruction)

    def generate(self, ast: Program) -> List[TACInstruction]:
        """Starts the IR generation process by visiting the AST."""
        self.visit(ast)
        return self.instructions

    def visit(self, node):
        """Generic visitor method for AST nodes."""
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Fallback for unhandled AST nodes."""
        raise NotImplementedError(f"IR generation not implemented for {type(node).__name__}")

    # Specific visitor methods for AST nodes:

    def visit_Program(self, node: Program):
        for statement in node.statements:
            self.visit(statement)

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        # For 'let x = 10;'
        if node.initializer:
            # Generate TAC for the initializer expression
            initializer_temp = self.visit(node.initializer)
            # Assign the result to the variable
            self.emit(TACInstruction('ASSIGN', initializer_temp, result=node.identifier))
        else:
            # For 'let x;' - simply declare (or initialize to default if language requires)
            # For now, no explicit TAC for simple declaration without initializer
            pass

    def visit_AssignmentStatement(self, node: AssignmentStatement):
        # For 'x = 20;'
        # Generate TAC for the expression on the right-hand side
        expr_temp = self.visit(node.expression)
        # Assign the result to the variable
        self.emit(TACInstruction('ASSIGN', expr_temp, result=node.identifier))

    def visit_LiteralExpression(self, node: LiteralExpression) -> str:
        # For literals like '10', 'true', 'false', '"hello"'
        # Literals are their own "result"
        return str(node.value) # Return the string representation of the literal

    def visit_BinaryOperation(self, node: BinaryOperation) -> str:
        # For 'a + b'
        left_temp = self.visit(node.left)
        right_temp = self.visit(node.right)
        result_temp = self.new_temp()
        self.emit(TACInstruction(node.operator.upper(), left_temp, right_temp, result=result_temp))
        return result_temp # Return the temporary holding the result of this operation

    # ... (Other visitor methods for control flow, function calls, etc.)
```

## 5. Implementation Details

The implementation will proceed as follows:

1.  **Create `compiler/ir_generator.py`:** This file will house the `TACInstruction` class and the `IRGenerator` class.
2.  **Integrate `IRGenerator` into `main.py`:** A new option will be added to the CLI to trigger intermediate code generation. This will involve:
    *   Parsing the input code to get the AST.
    *   Instantiating `IRGenerator`.
    *   Calling `generate` on the AST.
    *   Printing the generated TAC instructions.
3.  **Refine `IRGenerator` Visitors:** As we introduce more language constructs (e.g., `if` statements, `while` loops, function calls), we will add corresponding `visit_` methods to the `IRGenerator` to emit the appropriate TAC instructions, including labels and jumps for control flow.
4.  **Testing:** Comprehensive tests will be written to ensure that the generated TAC accurately reflects the semantics of the input code.

This structured approach will allow us to systematically build out the intermediate code generation capabilities of our compiler.
