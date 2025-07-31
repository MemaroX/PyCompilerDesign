from typing import List
from compiler.ir_generator import TACInstruction

class Optimizer:
    def __init__(self):
        pass

    def optimize(self, tac_instructions: List[TACInstruction], max_passes: int = 1) -> (List[TACInstruction], List[str]):
        optimizations_applied = []
        current_instructions = list(tac_instructions)

        for _ in range(max_passes):
            optimized_instructions_pass = []
            constants = {}
            pass_applied_optimization = False

            for tac in current_instructions:
                print(f"DEBUG OPT: Processing TAC: {tac}")
                # Helper to get the actual value of an argument (either a literal or a constant from the table)
                def get_value(arg):
                    if isinstance(arg, (int, float)):
                        return arg
                    if isinstance(arg, str):
                        if arg in constants:
                            return constants[arg]
                        try:
                            return int(arg)
                        except ValueError:
                            try:
                                return float(arg)
                            except ValueError:
                                pass
                    return arg # Not a constant or known variable

                if tac.op in ['ADD', 'SUB', 'MUL', 'DIV']:
                    print(f"DEBUG OPT:   Original tac.arg1: {tac.arg1} (type: {type(tac.arg1).__name__}), tac.arg2: {tac.arg2} (type: {type(tac.arg2).__name__})") # NEW DEBUG
                    arg1_val = get_value(tac.arg1)
                    arg2_val = get_value(tac.arg2)
                    print(f"DEBUG OPT:   arg1_val: {arg1_val} (type: {type(arg1_val).__name__}), arg2_val: {arg2_val} (type: {type(arg2_val).__name__})")
                    print(f"DEBUG OPT:   Checking isinstance: arg1_val is int/float: {isinstance(arg1_val, (int, float))}, arg2_val is int/float: {isinstance(arg2_val, (int, float))}") # NEW DEBUG LINE

                    if isinstance(arg1_val, (int, float)) and isinstance(arg2_val, (int, float)):
                        # Attempt to constant fold
                        if tac.op == 'DIV' and arg2_val == 0:
                            # Division by zero, cannot constant fold
                            optimized_instructions_pass.append(tac)
                            print(f"DEBUG OPT:   Division by zero, keeping original. Optimized instructions: {optimized_instructions_pass}")
                            continue
                        else:
                            # Perform the operation
                            if tac.op == 'ADD':
                                result_val = arg1_val + arg2_val
                            elif tac.op == 'SUB':
                                result_val = arg1_val - arg2_val
                            elif tac.op == 'MUL':
                                result_val = arg1_val * arg2_val
                            elif tac.op == 'DIV':
                                result_val = arg1_val / arg2_val

                            # Successfully folded
                            new_tac = TACInstruction('ASSIGN', result_val, result=tac.result)
                            optimized_instructions_pass.append(new_tac)
                            constants[tac.result] = result_val
                            optimizations_applied.append(f"Constant folded '{tac.arg1} {tac.op_symbol()} {tac.arg2}' to '{result_val}'")
                            pass_applied_optimization = True
                            print(f"DEBUG OPT:   Folded to: {new_tac}. Constants: {constants}. Optimized instructions: {optimized_instructions_pass}")
                            continue
                    else:
                        # Not all arguments are constants, keep original instruction
                        optimized_instructions_pass.append(tac)
                        print(f"DEBUG OPT:   Not all constants, keeping original. Optimized instructions: {optimized_instructions_pass}")

                elif tac.op == 'ASSIGN':
                    assigned_value = get_value(tac.arg1)
                    print(f"DEBUG OPT:   Assigned value: {assigned_value} (type: {type(assigned_value).__name__})")
                    
                    if isinstance(assigned_value, (int, float, str)):
                        # If assigning a constant, record it and emit a direct assign
                        constants[tac.result] = assigned_value
                        optimized_instructions_pass.append(TACInstruction('ASSIGN', assigned_value, result=tac.result))
                        if tac.arg1 != assigned_value: # Check if actual change occurred
                            optimizations_applied.append(f"Propagated constant '{assigned_value}' to '{tac.result}'")
                            pass_applied_optimization = True
                        print(f"DEBUG OPT:   Assigned constant. Constants: {constants}. Optimized instructions: {optimized_instructions_pass}")
                        continue
                    else:
                        # If assigning a non-constant, remove from constants table and keep original instruction
                        if tac.result in constants:
                            del constants[tac.result]
                        optimized_instructions_pass.append(tac)
                        print(f"DEBUG OPT:   Assigned non-constant. Constants: {constants}. Optimized instructions: {optimized_instructions_pass}")
                else:
                    # Other instructions are passed through unchanged
                    optimized_instructions_pass.append(tac)
                    print(f"DEBUG OPT:   Other instruction, keeping original. Optimized instructions: {optimized_instructions_pass}")
            
            if not pass_applied_optimization:
                break # No optimizations applied in this pass, stop iterating
            current_instructions = optimized_instructions_pass

        return current_instructions, optimizations_applied
