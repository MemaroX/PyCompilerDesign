from compiler.lexer.lexer import CppLexer
from compiler.parser import Parser
import sys

if __name__ == "__main__":
    sample_code = '''
    int x = 5;
    int y = 10;
    int z = 2 + 3 * 4;
    '''
    
    choice = input("Enter '1' to use sample code, or '2' to enter your own code: ")
    
    code_to_lex = ""
    if choice == '1':
        code_to_lex = sample_code
    elif choice == '2':
        print("Enter your C++ code and press Ctrl+D (Unix) or Ctrl+Z then Enter (Windows) to finish:")
        code_to_lex = sys.stdin.read()
    else:
        print("Invalid choice. Using sample code.")
        code_to_lex = sample_code

    lexer = CppLexer(code_to_lex)
    tokens = lexer.tokenize_and_filter(include_comments=False, include_newlines=False)

    parser = Parser(tokens)
    program = parser.parse()

    if parser.errors:
        print("Parser errors:")
        for error in parser.errors:
            print(error)
    else:
        print("AST:")
        print(program)