from typing import List, Dict, Any

class CodeGenerator:
    """
    Generates a simple assembly-like code from Three-Address Code (TAC).
    """
    def __init__(self):
        self.assembly_code = []
        self.register_map: Dict[str, str] = {}
        self.register_counter = 0

    def _get_register(self, variable: str) -> str:
        """Allocates or retrieves a register for a TAC variable."""
        if variable not in self.register_map:
            self.register_counter += 1
            self.register_map[variable] = f"R{self.register_counter}"
        return self.register_map[variable]

    def generate(self, tac_instructions: List[Dict[str, Any]]) -> List[str]:
        """
        Generates assembly code for a list of TAC instructions.
        """
        self.assembly_code = []
        self.register_map = {}
        self.register_counter = 0

        for tac in tac_instructions:
            op = tac.get('op')
            arg1 = tac.get('arg1')
            arg2 = tac.get('arg2')
            result = tac.get('result')

            if op in ['+', '-', '*', '/']:
                # Ensure operands are in registers
                reg1 = self._get_register(str(arg1)) if not str(arg1).isdigit() else None
                if reg1 is None: # It's a literal
                    reg1 = self._get_register(f"temp_{arg1}")
                    self.assembly_code.append(f"LOAD {reg1}, {arg1}")

                reg2 = self._get_register(str(arg2)) if not str(arg2).isdigit() else None
                if reg2 is None: # It's a literal
                    reg2 = self._get_register(f"temp_{arg2}")
                    self.assembly_code.append(f"LOAD {reg2}, {arg2}")
                
                op_map = {
                    '+': 'ADD',
                    '-': 'SUB',
                    '*': 'MUL',
                    '/': 'DIV'
                }
                assembly_op = op_map[op]
                
                result_reg = self._get_register(result)
                self.assembly_code.append(f"{assembly_op} {result_reg}, {reg1}, {reg2}")

            elif op == '=':
                # Handle assignment
                if str(arg1).isdigit() or str(arg1).startswith('"'): # Literal assignment
                    result_reg = self._get_register(result)
                    self.assembly_code.append(f"LOAD {result_reg}, {arg1}")
                else: # Variable to variable assignment
                    arg1_reg = self._get_register(arg1)
                    result_reg = self._get_register(result)
                    self.assembly_code.append(f"MOVE {result_reg}, {arg1_reg}")
            
            # For simplicity, we assume final variables are stored in registers.
            # A more complex generator would handle storing back to memory.

        # Add a final "STORE" for the last computed variable for clarity
        if tac_instructions:
            last_result = tac_instructions[-1].get('result')
            if last_result and last_result in self.register_map:
                 self.assembly_code.append(f"STORE {last_result}, {self.register_map[last_result]}")


        return self.assembly_code
